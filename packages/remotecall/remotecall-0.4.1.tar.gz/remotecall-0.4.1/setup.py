import os
from setuptools import setup, find_packages

module_name = "remotecall"
meta = {}


with open(
    os.path.join(os.path.dirname(__file__), "src", module_name, "_meta.py"), "rt"
) as f:
    exec(f.read(), meta)  # pylint: disable=exec-used


setup(
    name=module_name,
    version=meta["__version__"],
    description="The module provides functionality to expose Python functions to be called remotely over ethernet.",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    url="https://gitlab.com/slaine/{}.git/".format(module_name),
    author=meta["__author__"],
    author_email="sami.jy.laine@gmail.com",
    entry_points={
        "console_scripts": ["main=remotecall.__main__:app"],
    },
    license=meta["__license__"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "requests >= 2.28.1",
    ],
    extras_require={
        "test": ["pytest"],
        "full": ["numpy", "pillow"],
        "numpycodec": ["numpy"],
        "imagecodec": ["pillow"],
    },
)
