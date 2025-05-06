from pathlib import Path
from types import ModuleType
from typing import Literal

Environment = Literal["local", "development", "test", "production"]

LOCAL: Environment = "local"
DEVELOPMENT: Environment = "development"
TEST: Environment = "test"
PRODUCTION: Environment = "production"

_ROOT: Path | None = None

def root(path: Path = Path(__file__)) -> Path:
    """
    Get the path of the directory where ".venv" is present.
    It discovers the root only once for the runtime, using a Singleton approach on module level.

    :param path: [Optional] an initial path to begin the search for the root.

    >>> issubclass(type(root()), Path)
    True
    """
    global _ROOT

    if not _ROOT:
        import glob

        if glob.glob(f"{path}/.*env") or glob.glob(f"{path}/main.py"):
            return path
        else:
            return root(path.parent.resolve())

    return _ROOT
