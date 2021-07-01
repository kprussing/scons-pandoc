import filecmp
import pathlib
import re
import shutil
import subprocess

import nox


@nox.session
def flake8(session):
    """Run flake8"""
    session.install("flake8")
    session.run("flake8", "sconscontrib", "noxfile.py")


@nox.session(venv_backend="conda")
@nox.parametrize(
    "python,scons", [
        (python, scons)
        for python in ("3.6", "3.7", "3.8", "3.9")
        for scons in ("3.0.5", "3.1.2", "4.1.0.post1")
        if scons < "4" or python >= "3.9"
    ],
)
@nox.parametrize(
    "panflute,pandoc", [("<2.0", ">=2.7,<2.10"), (">=2.0", ">2.10")]
)
def test(session, python, scons, panflute, pandoc):
    session.install(f"scons=={scons}", f"panflute{panflute}",
                    "import_metadata; python_version<'3.8'",
                    )
    session.conda_install(f"pandoc{pandoc}")

    root = pathlib.Path(__file__).parent
    dest = pathlib.Path(session.bin).parent

    # Work around the fact we can't install directly to scons<4.0
    scons_version = tuple(
        int(_) for _ in scons.split(".") if re.match(r"^\d+$", _)
    )
    if scons_version >= (4, 0):
        session.install(".")
        command = ["scons", "--no-site-dir"]
    else:
        site_tools = dest / "site_scons" / "site_tools"
        if not site_tools.is_dir():
            site_tools.mkdir(parents=True)

        if site_tools.joinpath("pandoc").is_dir():
            shutil.rmtree(site_tools / "pandoc")

        shutil.copytree(
            root / "sconscontrib" / "Scons" / "Tool" / "pandoc",
            site_tools / "pandoc"
        )
        command = ["scons"]

    # Document building
    session.install("numpy", "matplotlib")

    for src in root.joinpath("example").glob("*"):
        if src.suffix in (".html", ".png"):
            continue

        shutil.copy(src, dest)

    session.chdir(dest)
    session.run(*command, external=False)

    pandoc = pathlib.Path(session.bin) / "pandoc"
    proc = subprocess.run([str(pandoc.resolve()), "--version"],
                          capture_output=True,
                          text=True
                          )
    pandoc_version = re.match(r"pandoc\s*(\d+[.]\d+)",
                              proc.stdout,
                              re.IGNORECASE
                              ).group(1)
    if tuple(int(_) for _ in pandoc_version.split(".")) < (2, 10):
        tag = "-old"
    else:
        tag = ""

    assert filecmp.cmp(root / "example" / f"example{tag}.html",
                       dest / "example.html",
                       shallow=False)
