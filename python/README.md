# Standard BOM for Python

A Python library for creating and consuming documents in
[standard-bom format](https://sbom.siemens.io/latest/format.html).

This library is mainly a wrapper for the official
[cyclonedx-python-lib](https://github.com/CycloneDX/cyclonedx-python-lib/) library.

## Usage

- Read a Standard BOM from a JSON file:

    ```python
    from standardbom.parser import StandardBomParser

    bom = StandardBomParser.parse("sbom.json")
    ```

- Write a Standard BOM to a JSON file:

    ```python
    from standardbom.parser import StandardBomParser

    bom = ...
    StandardBomParser.save(bom, "sbom.json")
    ```

## Development

In order to build this library on your local PC, and/or contribute to this library, mind the following prerequisites:

- [Python](https://www.python.org/doc/versions/) > v3.8.1 - ideally > v3.10
- [Poetry](https://python-poetry.org/) > v1.3.0

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


- Check PEP-8 linting compliance with

    ```bash
    poetry run flake8
    ```


- Run all unit tests with

    ```bash
    poetry run coverage run --branch -m unittest discover -v
    ```
