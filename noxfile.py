import nox


@nox.session(python=["3.8", "3.7"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8", "codaio", "tests")
