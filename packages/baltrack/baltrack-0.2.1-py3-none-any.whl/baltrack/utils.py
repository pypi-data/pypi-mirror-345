import os

_sentinel = "NOT_GIVEN"


def getenv(name: str, default: str | None = _sentinel) -> str:
    try:
        return os.environ[f"BALTRACK_{name}"]
    except KeyError:
        return (
            os.environ[name]
            if default == _sentinel
            else os.getenv(name, default)
        )
