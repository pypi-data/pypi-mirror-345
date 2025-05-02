# setup.py
# This code is part of Qiskit.
#
# (C) Copyright Dr. Jeffrey Chijioke-Uche, 2025
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


import pathlib
from setuptools import setup, find_packages

# The directory containing this file
here = pathlib.Path(__file__).parent.resolve()

# Read the long description from README.md
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="qiskit-connector",
    version = "2.1.2",
    author="Dr. Jeffrey Chijioke-Uche",
    author_email="sj@chijioke-uche.com",
    description="Quantum Computing Qiskit Connector For Quantum Backend Use In Realtime",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/schijioke-uche/qiskit-connector",
    project_urls={
        "Homepage": "https://github.com/schijioke-uche/pypi-qiskit-connector",
        "Source":   "https://github.com/schijioke-uche/pypi-qiskit-connector",
        "Tracker":  "https://github.com/schijioke-uche/pypi-qiskit-connector/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Quantum Computing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["qiskit_connector", "qiskit_connector.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.32.3",
        "python-dotenv>=1.1.0",
        "qiskit-ibm-runtime>=0.38.0",
        "qiskit>=2.0.0",
    ],
    license="MIT-License",
    license_files=("LICENSE",),
)
