from setuptools import setup, find_packages
import sys

# data_files = []
# if sys.platform == "win32":
#     data_files = [('Scripts', ['scripts/ace.exe'])]

setup(
    name = "ACE-calc",
    packages = find_packages(),
    version = "0.1.0", 
    install_requires = [],
    python_requires = ">=3.6",
    author = "xystudio",
    author_email = "173288240@qq.com",
    description = "Fast calculate the cyclone ACE.",
    long_description = open("README.md",encoding="utf-8").read(),
    license = "MIT",
    url = "https://github.com/xystudio889/ACECalc",
    include_package_data = True
)
