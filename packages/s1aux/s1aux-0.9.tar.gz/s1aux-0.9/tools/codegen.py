#!/usr/bin/env python3

"""Command line tool for automatic generation of s1aux.parse code form XSDs."""

import os
import sys
import enum
import shutil
import difflib
import logging
import pathlib
import argparse
import warnings
import itertools
import subprocess
import collections
from xml.etree import ElementTree as etree  # noqa: N813
from urllib.parse import urlencode, urlparse
from collections.abc import Iterator

import tqdm
import requests

try:
    from os import EX_OK
except ImportError:
    EX_OK = 0
EX_FAILURE = 1
EX_INTERRUPT = 130


SAR_MPC_API_URL = "https://sar-mpc.eu/api/v1"
DEFAULT_QUERY_PARAMS = {
    "product_type__in": "AUX_PP1,AUX_CAL,AUX_INS,AUX_PP2,AUX_SCF,AUX_ITC",
    "sentinel1__mission": "S1A",
    "sentinel1__instr_conf_id": "7",
    "adf__active": "true",
}
FULL_QUERY_PARAMS = {
    "product_type__in": "AUX_PP1,AUX_CAL,AUX_INS,AUX_PP2,AUX_SCF,AUX_ITC",
}


PathType = str | os.PathLike[str]


_log = logging.getLogger(__name__)
PROCESS_UNVERSIONED: bool = False


class ELayout(enum.Enum):
    """Layout of the package."""

    FLAT = "flat"
    NESTED = "nested"

    def __str__(self) -> str:
        return self.name


def query_url(url: str = SAR_MPC_API_URL, **kwargs: str) -> str:
    """Build the query for Sentinel-1 auxiliary products."""
    if len(kwargs) > 0:
        return f"{url}?{urlencode(kwargs)}"
    return url


def _download(url: str, outfile: PathType | None = None) -> pathlib.Path:
    if outfile is None:
        outfile = pathlib.Path(urlparse(url).path).name
    outfile = pathlib.Path(outfile)
    response = requests.get(url)
    response.raise_for_status()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_bytes(response.content)
    return outfile


def _iter_pages(url: str) -> Iterator[dict]:
    response = requests.get(url)
    response.raise_for_status()

    page_data = response.json()
    while page_data:
        yield page_data
        next_ = page_data.get("next")
        if next_:
            response = requests.get(next_)
            response.raise_for_status()
            page_data = response.json()
        else:
            page_data = None


def download_archive_metadata(
    query_params: dict[str, str] = DEFAULT_QUERY_PARAMS,
) -> dict[str, list]:
    """Download metadata of requested products from the archive."""
    query = query_url(**query_params)
    archive_json: dict[str, list] = {"results": []}
    for page, page_data in enumerate(_iter_pages(query)):
        _log.debug(
            "page: %s, count: %d, next: %s",
            page,
            page_data["count"],
            page_data["next"],
        )
        archive_json["results"].extend(page_data["results"])
    return archive_json


def download_aux_products(
    datadir: PathType = "data",
    query_params: dict[str, str] = DEFAULT_QUERY_PARAMS,
) -> pathlib.Path:
    """Download a base set of auxiliary products."""
    _log.info("query the archive")
    archive_data = download_archive_metadata(query_params=query_params)

    _log.info("download products")
    datadir = pathlib.Path(datadir)
    for product in tqdm.tqdm(archive_data["results"], unit="products"):
        url = product["remote_url"]
        outfile = datadir.joinpath(product["physical_name"])
        if not outfile.exists():
            _download(url, outfile=outfile)
            shutil.unpack_archive(outfile, extract_dir=outfile.parent)

    return datadir


def get_spec_version(product_dir: PathType) -> str | None:
    """Return the product specification version for the input aux product."""
    product_dir = pathlib.Path(product_dir)
    try:
        xsdfile = next(
            itertools.chain(
                product_dir.glob("support/s1-aux-*.xsd"),
                product_dir.glob("support/s1--aux-*.xsd"),  # TODO: check
            ),
        )
    except StopIteration:
        msg = f"No AUX XSD found in '{product_dir}'"
        warnings.warn(msg, stacklevel=2)  # TODO: check
        return None

    return etree.parse(xsdfile).getroot().attrib.get("version")


class _EChange(enum.IntFlag):
    NOCHANGE = 0
    LEFT = enum.auto()
    RIGHT = enum.auto()


def _detect_changes(left: str, right: str) -> _EChange:
    changed = _EChange.NOCHANGE
    for line in difflib.unified_diff(left.splitlines(), right.splitlines()):
        if line.startswith(("---", "+++")):
            continue

        change_marker = line[0]
        if change_marker == "-":
            changed |= _EChange.LEFT
        elif change_marker == "+":
            changed |= _EChange.RIGHT

    return changed


def _normalized_spec_version(
    spec_version: str, sep: str = ".", fallback: str = "v_.__"
) -> str:
    try:
        major, minor = (int(item) for item in spec_version.split("."))
    except ValueError:
        return fallback
    return f"v{major}{sep}{minor:02d}"


def _process_xsd(
    path: pathlib.Path,
    target_xsd_dir: pathlib.Path,
    strict: bool = False,
) -> None:
    dst = target_xsd_dir.joinpath(
        # TODO: check
        path.name.removeprefix("s1-aux-").removeprefix("s1--aux-")
    )
    if dst.exists():
        left_data = path.read_text()
        right_data = dst.read_text()
        if left_data != right_data:
            msg = (
                f"source ('{path}') and target ('{dst}') files "
                "have different content."
            )
            if strict:
                raise FileExistsError(msg)

            change = _detect_changes(left_data, right_data)
            if change is _EChange.LEFT:
                warnings.warn(f"{msg} Replace target.", stacklevel=1)
                shutil.copy(path, dst)
            elif change is _EChange.RIGHT:
                warnings.warn(f"{msg} Skip.", stacklevel=1)
            elif change == (_EChange.LEFT + _EChange.RIGHT):
                # both files have unique content
                raise FileExistsError(msg)
    else:
        shutil.copy(path, dst)


def make_xds_dir(
    datadir: PathType,
    xsd_dir: PathType = "xsd",
    layout: ELayout = ELayout.NESTED,
    strict: bool = False,
) -> pathlib.Path:
    """Populate the XSD diractory using aux products support data."""
    datadir = pathlib.Path(datadir)
    if not datadir.exists():
        raise FileNotFoundError(str(datadir))

    xsd_dir = pathlib.Path(xsd_dir)

    count = 0
    unversioned = collections.defaultdict(list)
    for product_dir in datadir.glob("S1?_AUX_*.SAFE"):
        spec_version = get_spec_version(product_dir)
        if spec_version is None:
            warnings.warn(
                "Unable to retrieve the specification version for "
                f"'{product_dir.name}', skip.",
                stacklevel=1,
            )
            gdate = product_dir.stem[29:38]
            unversioned[gdate].append(product_dir)
            continue

        count += 1

        if layout is ELayout.NESTED:
            target_xsd_dir = xsd_dir.joinpath(
                _normalized_spec_version(spec_version)
            )
        else:
            target_xsd_dir = xsd_dir

        target_xsd_dir.mkdir(parents=True, exist_ok=True)

        for path in product_dir.glob("**/*.xsd"):
            _process_xsd(path, target_xsd_dir, strict)

    if PROCESS_UNVERSIONED:
        unversioned_keys = sorted(
            key for key in unversioned.keys() if key >= "G20140909"
        )
        if layout is ELayout.NESTED:
            key = unversioned_keys[0]
            target_xsd_dir = xsd_dir.joinpath(key)
        else:
            target_xsd_dir = xsd_dir

        for key in unversioned_keys:
            for product_dir in unversioned[key]:
                target_xsd_dir.mkdir(parents=True, exist_ok=True)
                try:
                    for path in product_dir.glob("**/*.xsd"):
                        _process_xsd(path, target_xsd_dir, strict)
                except FileExistsError:
                    if layout is ELayout.NESTED:
                        target_xsd_dir = xsd_dir.joinpath(key)
                    else:
                        target_xsd_dir = xsd_dir
                    target_xsd_dir.mkdir(parents=True, exist_ok=True)

                    for path in product_dir.glob("**/*.xsd"):
                        try:
                            _process_xsd(path, target_xsd_dir, strict)
                        except FileExistsError as exc:
                            warnings.warn(str(exc), stacklevel=1)

                count += 1

    if count < 1:
        raise FileNotFoundError(f"No XSD files found in {xsd_dir}")

    return xsd_dir


def make_cmd(
    xsd_dir: PathType,
    config_file: PathType = ".xsdata.xml",
    package_name: str = "s1aux.parse",
) -> list[str]:
    """Generate the command for xsdata execution."""
    config_file = pathlib.Path(config_file)

    cmd = ["xsdata", "-r"]
    if config_file.exists():
        cmd.extend(["-c", os.fspath(config_file)])
    else:
        default_cmd_args = [
            "--relative-imports",
            "--include-header",
            "--frozen",
            "--slots",
            "--kw-only",
            "-ds",
            "NumPy",
            "-ss",
            "filenames",
        ]
        cmd.extend(default_cmd_args)
    cmd.extend(["-p", package_name])
    cmd.append(os.fspath(xsd_dir))

    return cmd


def generate_s1aux_package_core(
    xsd_dir: PathType,
    package_name: str = "s1aux.parse",
    *,
    config_file: PathType = ".xsdata.xml",
    overwrite: bool = False,
    quiet: bool = True,
) -> str:
    """Generate the Python package for s1aux using xsdata and input XSDs."""
    package_path = pathlib.Path().joinpath(*package_name.split("."))
    if package_path.exists() and not overwrite:
        raise FileExistsError(package_name)

    cmd = make_cmd(xsd_dir, config_file, package_name)

    subprocess.run(cmd, check=True, capture_output=quiet)

    return package_name


def generate_s1aux_package(
    xsd_dir: PathType,
    package_name: str = "s1aux.parse",
    *,
    config_file: PathType = ".xsdata.xml",
    overwrite: bool = False,
    quiet: bool = True,
) -> str:
    """Generate the Python package for s1aux using xsdata and input XSDs."""
    xsd_dir = pathlib.Path(xsd_dir)

    if len(list(xsd_dir.glob("*.xsd"))) > 0:
        layout = ELayout.FLAT
    else:
        layout = ELayout.NESTED
    _log.info("layout: %s", layout)

    if layout is ELayout.FLAT:
        return generate_s1aux_package_core(
            xsd_dir,
            package_name,
            config_file=config_file,
            overwrite=overwrite,
            quiet=quiet,
        )

    for versioned_xsd_dir in xsd_dir.glob("v[0-9].*"):
        _log.info("versioned_xsd_dir: %s", versioned_xsd_dir)

        normalized_version = versioned_xsd_dir.name.replace(".", "_")
        versioned_package_name = f"{package_name}.{normalized_version}"
        _log.info("package_name: %s", versioned_package_name)

        generate_s1aux_package_core(
            versioned_xsd_dir,
            versioned_package_name,
            config_file=config_file,
            overwrite=overwrite,
            quiet=quiet,
        )

    if PROCESS_UNVERSIONED:
        for versioned_xsd_dir in xsd_dir.glob("G*"):
            _log.info("versioned_xsd_dir: %s", versioned_xsd_dir)

            normalized_version = str(versioned_xsd_dir)
            versioned_package_name = f"{package_name}.{normalized_version}"
            _log.info("package_name: %s", versioned_package_name)

            generate_s1aux_package_core(
                versioned_xsd_dir,
                versioned_package_name,
                config_file=config_file,
                overwrite=overwrite,
                quiet=quiet,
            )

    return package_name


__version__ = "1.0"
PROG = pathlib.Path(__file__).stem
LOGFMT = "%(asctime)s %(levelname)-8s -- %(message)s"
DEFAULT_LOGLEVEL = "WARNING"


def _autocomplete(parser: argparse.ArgumentParser) -> None:
    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)


def _add_logging_control_args(
    parser: argparse.ArgumentParser, default_loglevel: str = DEFAULT_LOGLEVEL
) -> argparse.ArgumentParser:
    """Add command line options for logging control."""
    loglevels = [logging.getLevelName(level) for level in range(10, 60, 10)]

    parser.add_argument(
        "--loglevel",
        default=default_loglevel,
        choices=loglevels,
        help="logging level (default: %(default)s)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="loglevel",
        action="store_const",
        const="ERROR",
        help=(
            "suppress standard output messages, "
            "only errors are printed to screen (set 'loglevel' to 'ERROR')"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        action="store_const",
        const="INFO",
        help="print verbose output messages (set 'loglevel' to 'INFO')",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="loglevel",
        action="store_const",
        const="DEBUG",
        help="print debug messages (set 'loglevel' to 'DEBUG')",
    )

    return parser


def get_parser() -> argparse.ArgumentParser:
    """Instantiate the command line argument (sub-)parser."""
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__)
    parser.add_argument(
        "--version", action="version", version="%(prog)s v" + __version__
    )

    # Command line options
    _add_logging_control_args(parser)

    parser.add_argument(
        "--offline",
        action="store_true",
        default=False,
        help=(
            "don't download AUX data from the internet. "
            "If this option is enabled hen the AUX data are expected to "
            "be already in 'datadir'"
        ),
    )
    parser.add_argument(
        "--datadir",
        default="data",
        help=(
            "path to the directory where AUX data are downloaded "
            "(default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-x",
        "--xsd-dir",
        default="xsd",
        help=(
            "path to the directory where XSD files are stored "
            "(default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-l",
        "--layout",
        choices=ELayout,
        type=ELayout.__getitem__,
        default=ELayout.NESTED,
        help=(
            "layout for the generated package: "
            "FLAT puts all the generated modules in the target package, "
            "NESTED creates a sub-packages hierarchy according to the "
            "format specification version. Default: '%(default)s'"
        ),
    )
    parser.add_argument(
        "-c",
        "--config-file",
        default=".xsdata.xml",
        help="path to the xsdata configuration file (default: '%(default)s')",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="overwrite existing files",
    )
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        default=False,
        help="do not attempt to merge conflicting XSD files and raise error",
    )

    # Positional arguments
    parser.add_argument(
        "package_name",
        default="s1aux.parse",
        nargs="?",
        help="path to the output Python package (default: '%(default)s')",
    )

    _autocomplete(parser)

    return parser


def parse_args(
    args: list[str] | None = None,
    namespace: argparse.Namespace | None = None,
    parser: argparse.ArgumentParser | None = None,
) -> argparse.Namespace:
    """Parse command line arguments."""
    if parser is None:
        parser = get_parser()

    return parser.parse_args(args, namespace)


def main(*argv: str) -> int:
    """Implement the main CLI interface."""
    # setup logging
    logging.basicConfig(format=LOGFMT, level=DEFAULT_LOGLEVEL)
    logging.captureWarnings(True)
    log = logging.getLogger(__name__)

    # parse cmd line arguments
    args = parse_args(list(argv) if argv else None)

    # execute main tasks
    exit_code = EX_OK
    try:
        # NOTE: use the root logger to set the logging level
        logging.getLogger().setLevel(args.loglevel)

        quiet: bool = getattr(logging, args.loglevel) < logging.INFO

        if args.layout is ELayout.FLAT:
            query_params = DEFAULT_QUERY_PARAMS
        else:
            query_params = FULL_QUERY_PARAMS

        if args.offline:
            datadir = args.datadir
        else:
            datadir = download_aux_products(
                args.datadir, query_params=query_params
            )
        xsd_dir = make_xds_dir(
            datadir, args.xsd_dir, layout=args.layout, strict=args.strict
        )
        outdir = generate_s1aux_package(
            xsd_dir,
            args.package_name,
            config_file=args.config_file,
            overwrite=args.force,
            quiet=quiet,
        )
        log.info("%s package generated in '%s'", args.package_name, outdir)
    except Exception as exc:
        log.critical(
            "unexpected exception caught: %r %s", type(exc).__name__, exc
        )
        log.debug("stacktrace:", exc_info=True)
        exit_code = EX_FAILURE
    except KeyboardInterrupt:
        log.warning("Keyboard interrupt received: exit the program")
        exit_code = EX_INTERRUPT

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
