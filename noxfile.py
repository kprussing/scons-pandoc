import nox


@nox.session
def flake8(session):
    """Run flake8"""
    session.install("flake8")
    session.run("flake8", "__init__.py", "noxfile.py")
