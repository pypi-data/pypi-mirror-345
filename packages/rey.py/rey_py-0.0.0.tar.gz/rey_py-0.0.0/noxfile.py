"""Nox sessions for automated testing and checking."""

import nox
from nox.sessions import Session

# Default Python version to run tests against
DEFAULT_PYTHON_VERSION = "3.12"

# Location of the sessions for nox to run
nox.options.sessions = ["tests", "lint", "mypy"]


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def tests(session: Session) -> None:
    """Run the test suite with pytest.

    By default, only runs against Python 3.12.
    To run against other versions, use the `--python` flag:
    nox -s tests -- --python=3.11,3.12
    """
    session.install(".[dev]")

    # Run pytest
    session.run("pytest", *session.posargs, "--cov=rey", "--cov-report=term")


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def lint(session: Session) -> None:
    """Run the linter."""
    args = session.posargs or ["rey", "tests"]
    session.install("ruff")
    session.run("ruff", "check", *args)
    session.run("ruff", "format", "--check", *args)


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["rey", "tests"]
    session.install(".[dev]")
    session.run("mypy", *args)


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def docs(session: Session) -> None:
    """Build the documentation."""
    session.install(".[docs]")
    session.run("sphinx-build", "docs", "docs/_build/html")


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def build(session: Session) -> None:
    """Build the package."""
    session.install("build", "setuptools>=45", "setuptools_scm>=6.2", "wheel")
    session.run("python", "-m", "build")


@nox.session(python=[DEFAULT_PYTHON_VERSION])
def publish(session: Session) -> None:
    """Publish package to PyPI."""
    session.install("build", "twine", "setuptools>=45", "setuptools_scm>=6.2", "wheel")
    session.run("python", "-m", "build")
    session.run("twine", "check", "dist/*")
    session.run("twine", "upload", "dist/*")
