import filecmp
import pathlib
import shutil

import nox


@nox.session
def flake8(session):
    """Run flake8"""
    session.install("flake8")
    session.run("flake8", "__init__.py", "noxfile.py")


@nox.session(venv_backend="conda")
@nox.parametrize(
    "python,scons", [
        (python, scons)
        for python in ("3.6", "3.7", "3.8", "3.9")
        for scons in ("3.0.5", "3.1.2", "4.1.0.post1")
        if scons < "4" or python >= "3.9"
    ],
)
def test(session, python, scons):
    session.install(f"scons=={scons}", "panflute>=2.0")
    session.conda_install("pandoc")
    session.install(".")
    # Document building
    session.install("numpy", "matplotlib")
    root = pathlib.Path(__file__).parent
    dest = pathlib.Path(session.bin).parent

    for src in root.joinpath("example").glob("*"):
        if src.suffix in (".html", ".png"):
            continue

        shutil.copy(src, dest)

    session.chdir(dest)
    session.run("scons", external=False)
    assert filecmp.cmp(root / "example" / "example.html",
                       dest / "example.html",
                       shallow=False)
