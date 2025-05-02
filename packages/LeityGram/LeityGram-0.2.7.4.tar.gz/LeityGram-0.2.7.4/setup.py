from setuptools import setup, find_packages

setup(
    name="LeityGram",
    version="0.2.7.4",
    packages=find_packages(),
    install_requires=["aiohttp>=3.8.0"],
)