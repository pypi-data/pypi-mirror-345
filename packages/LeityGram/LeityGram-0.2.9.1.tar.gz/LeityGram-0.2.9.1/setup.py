from setuptools import setup, find_packages

setup(
    name="LeityGram",
    version="0.2.9.1",
    packages=find_packages(),
    install_requires=["aiohttp>=3.8.0"],
)