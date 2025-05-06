#!/usr/bin/env python3
"""Setup file for the ARL package."""

import os
from setuptools import find_packages, setup

# Get the version from palaestrai.__version__ without executing the module:
version = {}
with open(
    os.path.join(os.path.dirname(__file__), "src", "palaestrai", "version.py")
) as fp:
    exec(fp.read(), version)
VERSION = version["__version__"]

with open("VERSION", "w") as fp:
    fp.write(VERSION)

with open("README.rst") as freader:
    README = freader.read()

install_requirements = [
    # CLI
    "click~=8.1.7",
    "click-aliases~=1.0.5",
    "appdirs~=1.4.4",
    "tabulate~=0.9.0",
    "semver>=3,<4",
    # YAML, JSON
    "yamale~=5.2.1",
    "ruamel.yaml~=0.18.6",
    "simplejson~=3.19.3",
    "jsonpickle~=4.0.0",
    # Process and IPC handling
    "uvloop",
    "aiomultiprocess~=0.9.1",  # pinning required
    "setproctitle~=1.3.4",
    "pyzmq~=26.2.0",
    "nest_asyncio~=1.6.0",
    # Data handling and storage
    "pyzstd",
    "numpy~=1.26.4",  # pinning required
    "pandas~=2.1.4",  # pinning required
    "dask[dataframe]~=2024.12.0",
    "gymnasium~=1.0.0",
    "psycopg2-binary~=2.9.10",
    "SQLalchemy~=1.4.50",  # pinning required
    "sqlalchemy-utils~=0.41.1",  # pinning required
    # Documentation
    "pandoc~=2.4",
    # Scheduler
    "GPUtil~=1.4.0",
    "psutil~=6.1.0",
    "docker~=7.1.0",
]

influx_requirements = [
    "elasticsearch>=7.0.0",
    "influxdb-client[ciso]",
]

development_requirements = [
    "Cython~=3.0.11",
    # Tests
    "tox~=4.23.2",
    "robotframework~=6.1.1",  # pinning required
    "robotframework-stacktrace~=0.4.1",  # pinning required
    "pytest~=8.3.4",
    "pytest-asyncio~=0.24.0",
    "pytest-cov~=6.0.0",
    "coverage~=7.6.9",
    "lxml~=5.3.0",
    "mock~=5.1.0",
    "alchemy-mock~=0.4.3",
    # Linting
    "black~=24.10.0",  # pinning recommended
    # Type checking
    "mypy~=1.13.0",
    "types-click~=7.1.8",
    "types-setuptools~=75.6.0",
    # Documentation
    "sphinx~=7.4.7",  # pinning required
    "nbsphinx~=0.9.5",
    "furo~=2024.8.6",
    "ipython~=8.30.0",
    "ipykernel~=6.29.5",
    "plotly~=5.24.1",
    "eralchemy2~=1.4.1",
]

fullstack_requirements = [
    "palaestrai-arsenai~=3.5.0",
    "palaestrai-agents~=3.5.0",
    "palaestrai-environments~=3.5.0",
    "palaestrai-mosaik>=3.5.4",
    "midas-mosaik[arl]~=2.0.0",
]

fullstack_development_requirements = [
    "palaestrai-arsenai@git+https://gitlab.com/arl2/arsenai.git@development#egg=palaestrai-arsenai",
    "palaestrai-agents@git+https://gitlab.com/arl2/harl.git@development#egg=harl",
    "palaestrai-environments@git+https://gitlab.com/arl2/palaestrai-environments.git@development#egg=palaestrai-environments",
    "palaestrai-mosaik@git+https://gitlab.com/arl2/palaestrai-mosaik.git@main#egg=palaestrai-mosaik",
    "midas-mosaik[arl]@git+https://gitlab.com/midas-mosaik/midas.git@development#egg=midas_mosaik",
]

full_dev = development_requirements + fullstack_development_requirements

extras = {
    "dev": development_requirements,
    "full": fullstack_requirements,
    "influx": influx_requirements,
}

# This line gets removed for PyPi upload
# extras.update({"full-dev": full_dev})

setup(
    name="palaestrai",
    version=VERSION,
    description="A Training Ground for Autonomous Agents",
    long_description=README,
    author="The ARL Developers",
    author_email="eric.veith@offis.de",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=install_requirements,
    extras_require=extras,
    license="LGPLv2",
    url="http://palaestr.ai/",
    entry_points={
        "console_scripts": [
            "palaestrai = palaestrai.cli.manager:cli",
            "palaestrai-scheduler = palaestrai.cli.scheduler:scheduler_setup",
            "arl-apply-migrations = palaestrai.store.migrations.apply:main",
        ]
    },
    package_data={"palaestrai": ["run_schema.yaml", "py.typed"]},
    data_files=[
        ("etc/bash_completion.d/", ["palaestrai_completion.sh"]),
        ("etc/zsh_completion.d/", ["palaestrai_completion.zsh"]),
        ("etc/fish_completion.d/", ["palaestrai_completion.fish"]),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v2 (LGPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
