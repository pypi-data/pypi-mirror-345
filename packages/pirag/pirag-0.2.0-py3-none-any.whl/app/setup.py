import os, tomli
from setuptools import setup, find_packages

# Load requirements
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Get version from pyproject.toml
with open(os.path.join(os.path.dirname(__file__), '../pyproject.toml'), 'rb') as f:
    pyproject = tomli.load(f)
    version = pyproject["project"]["version"]

APP_NAME = "pirag"

setup(
    name = APP_NAME,
    version = version,
    packages = find_packages(),
    include_package_data = True,
    install_requires = requirements,
    entry_points = {
        "console_scripts": [
            f"{APP_NAME}=app.cli:main",
        ],
    },
)
