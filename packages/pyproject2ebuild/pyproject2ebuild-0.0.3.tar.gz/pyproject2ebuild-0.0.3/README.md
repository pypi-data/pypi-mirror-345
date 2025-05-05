# pyproject2ebuild

**pyproject2ebuild** is a tool to automatically convert Python `pyproject.toml` 
metadata into Gentoo ebuild files.
It can openrate on a local `pyproject.toml` or fetch it for you.

## Features
- Parses project name, version, description, license, homepage
- Converts Python dependencies to Gentoo dependency syntax
- Auto-maps version constraints
- Auto-generate metadata.xml
- Compatible with setuptools and setuptools_scm
- 
- GPL-3.0-or-later licensed



## Example:

```
$ pyproject2ebuild https://raw.githubusercontent.com/pyupio/safety/refs/heads/main/pyproject.toml
Downloaded pyproject.toml from https://raw.githubusercontent.com/pyupio/safety/refs/heads/main/pyproject.toml
Ebuild written to ./safety-3.4.0.ebuild


$ cat safety-3.4.0.ebuild
# Copyright 2025
# Distributed under the terms of the GNU General Public License v2

EAPI=8

PYTHON_COMPAT=( python3_11 python3_12 )

inherit distutils-r1

DESCRIPTION="Scan dependencies for known vulnerabilities and licenses."
HOMEPAGE=""
SRC_URI="https://pypi.io/packages/source/s/safety/safety-3.4.0.tar.gz"

LICENSE="MIT"
SLOT="0"
KEYWORDS="~amd64"

DEPEND="
	>=dev-python/authlib-1.2.0[${PYTHON_USEDEP}]
	>=dev-python/click-8.0.2[${PYTHON_USEDEP}]
	>=dev-python/dparse-0.6.4[${PYTHON_USEDEP}]
	>=dev-python/filelock-3.16.1[${PYTHON_USEDEP}]
	>=dev-python/jinja2-3.1.0[${PYTHON_USEDEP}]
	>=dev-python/marshmallow-3.15.0[${PYTHON_USEDEP}]
	>=dev-python/packaging-21.0[${PYTHON_USEDEP}]
	>=dev-python/psutil-6.1.0[${PYTHON_USEDEP}]
	>=dev-python/pydantic-2.6.0[${PYTHON_USEDEP}]
	<dev-python/pydantic-2.10.0[${PYTHON_USEDEP}]
	dev-python/requests[${PYTHON_USEDEP}]
	dev-python/httpx[${PYTHON_USEDEP}]
	dev-python/tenacity[${PYTHON_USEDEP}]
	=dev-python/safety-schemas-0.0.14[${PYTHON_USEDEP}]
	>=dev-python/setuptools-65.5.1[${PYTHON_USEDEP}]
	>=dev-python/typer-0.12.1[${PYTHON_USEDEP}]
	>=dev-python/typing-extensions-4.7.1[${PYTHON_USEDEP}]
	>=dev-python/nltk-3.9[${PYTHON_USEDEP}]
	dev-python/tomlkit[${PYTHON_USEDEP}]
"
RDEPEND="${DEPEND}"
```
