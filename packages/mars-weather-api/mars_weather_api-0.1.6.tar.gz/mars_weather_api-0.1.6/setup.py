# This is the setup script for the mars_weather_api package.
# It uses setuptools to define the package metadata and dependencies.

from setuptools import setup, find_packages

setup(
    name="mars_weather_api",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
)