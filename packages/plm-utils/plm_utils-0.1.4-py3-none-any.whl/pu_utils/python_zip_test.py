from pathlib import Path
from shutil import rmtree

from ward import test

from pu_utils.python_zip import pip_install, reproducible_zip, zip_source

PROJECT_DIR = Path(__file__).parents[1]
FIXTURES_DIR = PROJECT_DIR.joinpath("fixtures")
TMP_DIR = PROJECT_DIR.joinpath("tmp")


@test("`pip install ...` to a target directory", tags=["network"])
def _() -> None:
    target = TMP_DIR.joinpath("python-zip-pip-install-test")
    pip_install(FIXTURES_DIR.joinpath("python_zip_requirements.txt"), target)
    assert target.joinpath("attrs").exists()


@test("`uv pip install ...` to a target directory", tags=["network"])
def _() -> None:
    target = TMP_DIR.joinpath("python-zip-uv-pip-install-test")
    pip_install(FIXTURES_DIR.joinpath("python_zip_requirements.txt"), target)
    assert target.joinpath("attrs").exists()


@test("reproducible_zip() produces identical zip file when its content are the same")
def _() -> None:
    # Reproduce the same directory and zip it
    zip_path = TMP_DIR.joinpath("python_zip.repro.zip")
    tmp_dir = TMP_DIR.joinpath("repro")
    tmp_dir.mkdir(0o755, exist_ok=True)
    tmp_dir.joinpath("repro1.txt").write_bytes(b"First")
    tmp_dir.joinpath("repro2.txt").write_bytes(b"Second")
    # Prepare another directory with 2 files of the same content

    reproducible_zip(zip_path, tmp_dir)
    rmtree(tmp_dir.resolve())
    golden_path = FIXTURES_DIR.joinpath("repro.zip")
    assert Path(golden_path).read_bytes() == Path(zip_path).read_bytes()


@test("zip_source() creates a zip file from the provided directory")
def _() -> None:
    zip_source(
        "source",
        source=FIXTURES_DIR.joinpath("zip_source"),
        dest=TMP_DIR.joinpath("zip_source"),
    )
    assert TMP_DIR.joinpath("zip_source/source.zip").exists()
