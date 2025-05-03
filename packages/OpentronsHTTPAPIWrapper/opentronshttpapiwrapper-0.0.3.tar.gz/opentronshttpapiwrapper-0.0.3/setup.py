import re
from setuptools import setup, find_packages

def get_version():
    with open("OpentronsHTTPAPIWrapper/__init__.py", "r", encoding="utf-8") as f:
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', f.read())
        if match:
            return match.group(1)
        raise RuntimeError("Version info not found in __init__.py")

setup(
    name="OpentronsHTTPAPIWrapper",
    version=get_version(),
    description="Python wrapper for the Opentrons HTTP API",
    author="Daniel Persaud, Nis Fisker-Bødker",
    license="MIT",
    readme="README.md",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=["requests"],
    url="https://github.com/yourusername/my_project",
)
