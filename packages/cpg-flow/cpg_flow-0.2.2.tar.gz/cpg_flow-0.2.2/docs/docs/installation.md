# 🔨 Installation

## 🙋‍♀️ User Installation Instructions

The packages are hosted on:

![PyPI](https://img.shields.io/badge/-PyPI-black?style=for-the-badge&logoColor=white&logo=pypi&color=3776AB)

To include `cpg-flow` in your python project simply install either the latest stable version as layed out in the PyPi package page. =

This is as simple as running the following in your project python environment
```bash
pip install cpg-flow
```

For a specific version
```bash
pip install cpg-flow==0.1.2
```

We recommend making the appropriate choice for your individual project. Simply including `cpg-flow` in your dependency management system of choice will install the latest stable relase. But if neccessary you can pin the version. For example in your `pyproject.toml` file simply include the following:
```toml
dependencies = [
    "cpg-flow",         # latest OR
    "cpg-flow==0.1.2",  # pinned version
]
```

## 🛠️ Development Installation Instructions

These instructions are for contributors and developers on the `cpg-flow` project repository. Follow the following steps to setup your environment for development.

To install this project, you will need to have Python and `uv` installed on your machine:

![uv](https://img.shields.io/badge/-uv-black?style=for-the-badge&logoColor=white&logo=uv&color=3776AB&link=https://docs.astral.sh/uv/)
![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logoColor=white&logo=python&color=3776AB)

We use uv for dependency management which can sync your environment locally with the following command:

```bash
# Install the package using uv
uv sync
```

However, to setup for development we recommend using the makefile setup which will do that for you.

```bash
make init-dev # installs pre-commit as a hook
```

To install `cpg-flow` locally for testing the code as an editable dependency

```bash
make install-local
```

This will install cpg-flow a an editable dependency in your environment. However, sometimes it can be useful to test the package post-build.
```bash
make install-build
```

This will build and install the package as it would be distributed.

You can confirm which version of cpg-flow is installed by running
```bash
uv pip show cpg-flow
```

For an Editable package it should show the repo location on your machine under the `Editable:` key.
```bash
Name: cpg-flow
Version: 0.1.2
Location: /Users/whoami/cpg-flow/.venv/lib/python3.10/site-packages
Editable project location: /Users/whoami/cpg-flow
Requires: coloredlogs, cpg-utils, grpcio, grpcio-status, hail, ipywidgets, metamist, networkx, plotly, pre-commit, pyyaml
Required-by:
```

The build version (static until you rebuild) will look like the following.
```bash
Name: cpg-flow
Version: 0.1.2
Location: /Users/whoami/cpg-flow/.venv/lib/python3.10/site-packages
Requires: coloredlogs, cpg-utils, grpcio, grpcio-status, hail, ipywidgets, metamist, networkx, plotly, pre-commit, pyyaml
Required-by:
```

!!! tip
    To try out the pre-installed `cpg-flow` in a Docker image, find more information in the **[Docker](#docker)** section.

## 🚀 Build</a>

To build the project, run the following command:

```bash
make build
```

To make sure that you're actually using the installed build we suggest calling the following to install the build wheel.

```bash
make install-build
```
