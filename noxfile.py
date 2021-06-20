import filecmp
import pathlib
import shutil

import nox


@nox.session
def flake8(session):
    """Run flake8"""
    session.install("flake8")
    session.run("flake8", "__init__.py", "noxfile.py")


@nox.session(python=["3.6", "3.7", "3.8", "3.9"],
             venv_backend="conda")
def test(session):
    session.install("scons", "panflute")
    session.conda_install("pandoc")
    # Document building
    session.install("numpy", "matplotlib")
    root = pathlib.Path(__file__).parent
    dest = pathlib.Path(session.bin).parent

    tooldir = dest / "site_scons" / "site_tools"
    tooldir.mkdir(parents=True, exist_ok=True)
    shutil.copy("__init__.py", tooldir / "pandoc.py")

    for src in root.joinpath("example").glob("*"):
        if src.suffix in (".html", ".png"):
            continue

        shutil.copy(src, dest)

    session.chdir(dest)
    session.run("scons", external=False)
    assert filecmp.cmp(root / "example" / "example.html",
                       dest / "example.html",
                       shallow=False)
