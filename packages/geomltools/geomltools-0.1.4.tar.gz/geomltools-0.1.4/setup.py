

from setuptools import setup, find_packages

import pathlib
import re

def get_version():
    here = pathlib.Path(__file__).parent / "geomltools" / "__init__.py"
    text = here.read_text()
    match = re.search(r'^__version__ = ["\']([^"\']*)["\']', text, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Version not found")



setup(
    name="geomltools",  
    version=get_version(),
    author="Mohammad Ali Fneich",
    author_email="fneichmohamad@gmail.com",
    description="A Python library for spatial machine learning and geospatial analysis.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Fneich/geomltools",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

