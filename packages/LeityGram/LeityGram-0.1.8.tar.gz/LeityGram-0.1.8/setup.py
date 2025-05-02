from setuptools import setup, find_packages

setup(
    name="LeityGram",
    version="0.1.8",
    packages=find_packages(),
    install_requires=["aiohttp>=3.8.0"],
)