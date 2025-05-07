from os import environ
from pathlib import Path

ROOT: Path = Path(environ.get("KVLANG_TEST_ROOT", __file__)).parent.absolute()
