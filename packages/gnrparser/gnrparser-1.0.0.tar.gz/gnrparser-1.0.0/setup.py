from setuptools import setup, find_packages

setup(
    name="gnrparser",
    version="1.0.0",
    description="Parser for GNR (Game Notation Record) files.",
    author="BesBobowyy",
    packages=find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)