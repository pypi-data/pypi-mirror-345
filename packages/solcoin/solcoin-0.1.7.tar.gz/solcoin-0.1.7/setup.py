from setuptools import find_packages, setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='solcoin',
    packages=find_packages(include=['solcoin']),
    version='0.1.7',
    description="A package for Solana transactions token transactions",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='bear102',
    license='MIT',
    install_requires=["solders",
        "solana",
        "borsh_construct",
        "requests",
        "construct",
        "segment-analytics-python"],
    url='https://github.com/bear102/solcoin',
)