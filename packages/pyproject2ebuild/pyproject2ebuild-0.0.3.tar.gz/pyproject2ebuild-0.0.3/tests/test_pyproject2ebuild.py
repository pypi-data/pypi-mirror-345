import pytest
from pyproject2ebuild.main import parse_pyproject, map_dependencies_to_gentoo, generate_ebuild

class Args:

    def __init__(self, version=None):
        self.version = version


@pytest.fixture(scope="function")
def parsed_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[build-system]
requires = ["setuptools>=61", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "example_project"
version = "1.2.3"
description = "An example project"
license = {text = "MIT"}
dependencies = ["requests >=2.0,<3.0"]

[project.urls]
homepage = "https://acme.com"
source = "https://github.com/acme/acmecli"
""")
    args = Args()
    yield parse_pyproject(str(pyproject), args)


def test_parse_minimal_pyproject(parsed_pyproject):

    metadata = parsed_pyproject

    assert metadata["name"] == "example-project"
    assert metadata["version"] == "1.2.3"
    assert metadata["description"] == "An example project"
    assert metadata["license"] == "MIT"
    assert metadata["dependencies"] == ["requests >=2.0,<3.0"]

def test_dynamic_vesrion(tmp_path):
    """Test for `dynamic = ["version"]` in pyproject.toml"""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[build-system]
requires = ["setuptools>=61", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "example_project"
dynamic = ["version"]
description = "An example project"
license = {text = "MIT"}
dependencies = ["requests >=2.0,<3.0"]

[project.urls]
homepage = "https://acme.com"
source = "https://github.com/acme/acmecli"
""")
    args = Args()
    with pytest.raises(ValueError):
        parse_pyproject(str(pyproject), args)

    args = Args(version="1.2.3")

    metadata = parse_pyproject(str(pyproject), args)
    assert metadata["version"] == "1.2.3"


def test_map_dependencies_to_gentoo():
    deps = [
        "requests >=2.25,<3.0",
        "flask ==2.0.1",
        "pytest"
    ]
    gentoo_deps = map_dependencies_to_gentoo(deps)

    assert ">=dev-python/requests-2.25[${PYTHON_USEDEP}]" in gentoo_deps
    assert "<dev-python/requests-3.0[${PYTHON_USEDEP}]" in gentoo_deps
    assert "=dev-python/flask-2.0.1[${PYTHON_USEDEP}]" in gentoo_deps
    assert "dev-python/pytest[${PYTHON_USEDEP}]" in gentoo_deps


def test_generate_ebuild_format():
    metadata = {
        "name": "example-project",
        "version": "1.2.3",
        "description": "Example Project",
        "homepage": "https://example.com",
        "license": "MIT",
        "dependencies": ["requests >=2.0,<3.0"],
        "build_backend": "hatchling"
    }

    ebuild = generate_ebuild(metadata)

    assert "DESCRIPTION=\"Example Project\"" in ebuild
    assert "HOMEPAGE=\"https://example.com\"" in ebuild
    assert ">=dev-python/requests-2.0[${PYTHON_USEDEP}]" in ebuild
    assert "<dev-python/requests-3.0[${PYTHON_USEDEP}]" in ebuild
    assert "DEPEND" in ebuild


def test_parse_no_deps_pyproject(parsed_pyproject):
    metadata = parsed_pyproject
    metadata['dependencies'] = []
    ebuild = generate_ebuild(metadata)

    assert "DEPEND" not in ebuild
    assert "BDEPEND" not in ebuild
