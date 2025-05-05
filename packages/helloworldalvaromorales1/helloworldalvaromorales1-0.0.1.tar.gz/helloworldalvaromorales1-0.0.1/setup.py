import setuptools
from pathlib import Path

long_description = Path("README.md").read_text()

setuptools.setup(
    name="helloworldalvaromorales1",
    version="0.0.1",
    author="Álvaro Morales",
    long_description=long_description,
    packages=setuptools.find_packages( 
        exclude=["mocks", "tests"]
    )
)
