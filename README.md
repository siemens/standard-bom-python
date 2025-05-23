# Standard BOM for Python

[![build](https://github.com/siemens/standard-bom-python/actions/workflows/ci.yml/badge.svg)](https://github.com/siemens/standard-bom-python/actions/workflows/ci.yml)
[![GitHub Tag](https://img.shields.io/github/v/tag/siemens/standard-bom-python)](https://github.com/siemens/standard-bom-python/releases/latest)

A Python library for creating and consuming documents in
[standard-bom format](https://sbom.siemens.io/latest/format.html).

This library is mainly a wrapper for the official [cyclonedx-python-lib](https://github.com/CycloneDX/cyclonedx-python-lib/) library with Standard BOM support.
"Standard BOM" is our Siemens-internal SBOM format.
Every Standard BOM document is a 100% CycloneDX document, so both CycloneDX and Standard BOM formats are supported.

## Installation

To install the library, run following command ...

... for pip:

```shell
pip install siemens-standard-bom
```

... for Poetry:

```shell
poetry add siemens-standard-bom
```

The library provides Standard BOM parser and serializer classes. The parser class is used to read a Standard BOM from a file, and the serializer class is used to write a Standard BOM to a file.

> 💡 **Hint:**
  This library provides strict type checking using [mypy](https://mypy.readthedocs.io/en/stable/).
  Using [mypy with strict type checks](https://mypy.readthedocs.io/en/stable/existing_code.html#introduce-stricter-options) in your own codebase is recommended to ensure type safety.

## Read a Standard BOM from a JSON file

```python
from siemens_standard_bom.parser import StandardBomParser

bom = StandardBomParser.parse("sbom.cdx.json")
```

## Write a Standard BOM to a JSON file

```python
from siemens_standard_bom.parser import StandardBomParser

bom = ...
StandardBomParser.save(bom, "sbom.cdx.json")
```

If you'd like to skip the `.dependencies` field in the output file, you can use the following code:

```python
from siemens_standard_bom.parser import StandardBomParser

bom = ...
StandardBomParser.save(bom, "sbom.cdx.json", with_dependencies=False)
```

This will save the Standard BOM to the file without the `.dependencies` field, which is `prohibited` in the
[`external` profile](https://sbom.siemens.io/v3/profiles.html).

## Create a Standard BOM document programmatically

The `StandardBom` class is a subclass of the `cyclonedx.bom.Bom` class from the upstream library
[cyclonedx-python-lib](https://github.com/CycloneDX/cyclonedx-python-lib) since this library is a wrapper of the
model objects from the upstream library.

```python
from siemens_standard_bom.model import StandardBom, Component, ComponentType
from cyclonedx.model.contact import OrganizationalContact

bom = StandardBom()
bom.add_author(OrganizationalContact(name='John Doe'))
bom.add_tool(Component(name='Sample Tool', version='1.0.0', type=ComponentType.APPLICATION))
bom.add_component(Component(name='Sample Component', version='1.2.3', type=ComponentType.LIBRARY))
```

You can also use the Standard BOM wrapper classes to create and edit the Standard BOM document.
For example, you can do the following similar to the example abode:

```python
from siemens_standard_bom.model import StandardBom, Component, ComponentType, SbomComponent
from cyclonedx.model.contact import OrganizationalContact

bom = StandardBom()
bom.add_author(OrganizationalContact(name='John Doe'))
bom.add_tool(SbomComponent(Component(name='Sample Tool', version='1.0.0', type=ComponentType.APPLICATION)))
bom.add_component(SbomComponent(Component(name='Sample Component', version='1.2.3', type=ComponentType.LIBRARY)))
```

## Retrieve fields from the Standard BOM object

Once you retrieve several fields from the `StandardBom` object, you get the wrapped Standard BOM types for these
fields. For example, the `tools` or `components` getters returns a list of `SbomComponent` objects:

```python
from typing import Iterable
from siemens_standard_bom.model import SbomComponent

bom = ...
components: Iterable[SbomComponent] = bom.components
tools: Iterable[SbomComponent] = bom.tools
```

## Setting licenses to a component

You can set licenses to a component by using the `licenses` setter method of the `SbomComponent`
class. `SbomComponent.licenses` setter method accepts an iterable of type `License` which can be a `LicenseExpression` or a `DisjunctiveLicense`:

```python
from cyclonedx.model.license import LicenseExpression

component = SbomComponent(...)
licenses = [LicenseExpression(value="MIT")]
component.licenses = licenses
```

## Development

In order to build this library on your local PC, and/or contribute to this library, mind the following prerequisites:

- [Python](https://www.python.org/doc/versions/) >=3.10, <4.0
- [Poetry](https://python-poetry.org/) >= v2.0

---
Once you have those prerequisites you can perform following development tasks locally:

- Run the build by executing

    ```bash
    poetry install
    ```

    then

    ```bash
    poetry build
    ```

    This will generate the build artifacts under `dist/` folder.

- Run all unit tests with all test cases and static code analysis

    ```bash
    poetry run tox run
    ```

    This will run all the tests for all supported Python versions as well as static linting and type checking.

## License

This project is Inner Source under the [MIT license](LICENSE) (SPDX-License-Identifier: MIT).

Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
