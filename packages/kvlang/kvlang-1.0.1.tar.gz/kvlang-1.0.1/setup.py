from pathlib import Path
from setuptools import setup, find_packages, Command
from typing import Mapping as M, List, Union, Collection, Dict


class Style(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sh import pycodestyle  # type: ignore
        pycodestyle("--ignore=none", "--exclude=modules", ".")


class Type(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sh import mypy  # type: ignore
        mypy("--exclude", "modules", "--exclude", "build", ".")


class Docs(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sh import sphinx_apidoc, make  # type: ignore
        sphinx_apidoc("-o", "docs", "kvlang", "kvlang/tests")
        make("-C", "docs", "clean", "html")


NAME = "kvlang"
VERSION = "1.0.1"
ROOT = Path(__file__).parent
KWARGS: M[str, str | bool | object] | M[str, Collection[str]] = {
    "name": NAME,
    "version": VERSION,
    "packages": find_packages(exclude=["*.tests"]),
    "license": "MIT",
    "long_description": (ROOT / "README.md").read_text(),
    "long_description_content_type": "text/markdown",
    "author": "Peter Badida",
    "author_email": "keyweeusr@gmail.com",
    "url": f"https://github.com/KeyWeeUsr/{NAME}",
    "download_url": (
        f"https://github.com/KeyWeeUsr/{NAME}/tarball/{VERSION}"
    ),
    "install_requires": ["lark>=1.2.2"],
    "extras_require": {
        "dev": [
            "pycodestyle", "pylint", "mypy",
            "types-setuptools", "sh", "sphinx"
        ],
        "kivy": [
            "kivy>=2.3.1"
        ],
        "release": ["wheel", "twine", "sh"]
    },
    "package_data": {
        "kvlang": ["*.lark"]
    },
    "include_package_data": True,
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only"
    ],
    "cmdclass": {
        "style": Style, "type": Type, "docs": Docs
    }
}


if __name__ == "__main__":
    setup(**KWARGS)
