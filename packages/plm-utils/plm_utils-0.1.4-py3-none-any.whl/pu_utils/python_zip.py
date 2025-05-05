import subprocess
from pathlib import Path
from shutil import rmtree
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def pip_install(requirements_path: str | Path, target_path: str | Path) -> None:
    requirements_path = Path(requirements_path)
    target_path = Path(target_path)

    target_path.parent.mkdir(0o755, exist_ok=True)
    rmtree(target_path, ignore_errors=True)
    command = [
        "pip",
        "install",
        "--target",
        target_path,
        "-r",
        requirements_path,
        "--only-binary",
        ":all:",
        "--platform",
        "manylinux2014_x86_64",
        "--implementation",
        "cp",
    ]
    process = subprocess.run(command, capture_output=True, check=False)
    if process.returncode != 0:
        print(process.stderr.decode())  # noqa: T201
        process.check_returncode()


def reproducible_zip(
    zip_path: str | Path,
    source_path: Path,
    prefix: Path | None = None,
) -> None:
    """
    Create a reproducible zip from the specified directory

    Reproducible here means using the same source and create two zip files,
    they will be bit-by-bit identical.

    The problem with zipping normally is file timestamps will be stored inside the zip.
    This leads to non-identical bits even though the content of the files being zipped
    is exactly the same. This function addresses that by using a fixed timestamp.
    """
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for p in sorted(source_path.glob("**/*")):
            if p.is_dir() or "__pycache__" in p.parts:
                continue
            path = p.relative_to(source_path)
            if prefix:
                path = Path(prefix).joinpath(path)
            zf.writestr(ZipInfo(str(path)), p.read_bytes())


def zip_source(
    name: str,
    source: str | Path,
    dest: str | Path,
    prefix: str | Path | None = None,
) -> Path:
    """
    Create a zip file from files in the directory specified in `source` and place the
    output zip in the directory specified in `dest`

    :param name:
        Name for this source. This name will be used as part of the final zip name

    :param source:
        The directory to be zipped

    :param dest:
        The directory to put the generated zip file in

    :param prefix:
        The prefix for files added to the zip file. For example, we can add `a.py`
        to the zip file as `x/a.py`

    :return:
        Path to the output zip
    """
    dest = Path(dest)
    dest.mkdir(mode=0o755, exist_ok=True)
    zip_path = dest.joinpath(f"{name}.zip")

    reproducible_zip(
        zip_path=zip_path,
        source_path=Path(source),
        prefix=Path(prefix) if prefix else None,
    )
    return zip_path
