"""LLM-Probe: A framework for probing LLMs."""

import importlib
import os
import sys

import packaging.version
import tomli
from setuptools import find_packages, setup

version_module_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "llm_probe", "version.py")
spec = importlib.util.spec_from_file_location("version", version_module_path)  # type: ignore
version_module = importlib.util.module_from_spec(spec)  # type: ignore
sys.modules["version"] = version_module
spec.loader.exec_module(version_module)  # type: ignore
version_content = version_module.__version__
package_version = packaging.version.parse(version_content)
setup.version = str(package_version)

# Read dependencies from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

setup(
    name=pyproject["project"]["name"],
    version=setup.version,
    description=pyproject["project"]["description"],
    author=pyproject["project"]["authors"][0]["name"],
    author_email=pyproject["project"]["authors"][0]["email"],
    packages=find_packages(include=["llm_probe", "llm_probe.*"]),
    zip_safe=False,
    install_requires=pyproject["project"]["dependencies"],
    include_package_data=True,
)
