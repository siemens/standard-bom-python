# AGENTS.md

Library wrapping [`cyclonedx-python-lib`](https://github.com/CycloneDX/cyclonedx-python-lib) to 
read/write Siemens [Standard BOM](https://sbom.siemens.io/latest/format.html) 
(a CycloneDX-compatible SBOM format). Source in [`siemens_standard_bom/`](siemens_standard_bom/).

## Commands (run from repo root)

- Full check (lint + type + tests, Python 3.10-3.14): `poetry run tox run`
- Lint + types only: `poetry run tox run -e lint,type`
- Tests on one interpreter: `poetry run tox run -e 3.12`
- Single test: `poetry run python -m unittest tests.test_v3_parser.SbomV3ParserTestCase.test_read_sunny_day`

Config: 
- [`tox.toml`](tox.toml), 
- [`pyproject.toml`](pyproject.toml), 
- [`.flake8`](.flake8), 
- [`.mypy.ini`](.mypy.ini).

## Testing

- Uses stdlib [`unittest`](https://docs.python.org/3/library/unittest.html) (via `unittest discover`), 
    NOT [pytest](https://docs.pytest.org/).
- Run from repo root only: tests read fixtures by relative path ([`tests/v2/`](tests/v2/), 
    [`tests/v3/`](tests/v3/)) and write to `output/` at repo root (gitignored, auto-created).
- Comparison tests use [`deepdiff`](https://github.com/seperman/deepdiff) and intentionally exclude 
    `bom_ref` values from diffs ([`tests/abstract_sbom_compare.py`](tests/abstract_sbom_compare.py)).

## Architecture

- Thin wrapper: `StandardBom` wraps `cyclonedx.model.bom.Bom`; `SbomComponent`/`SourceArtifact`
    /`ExternalComponent` wrap CycloneDX models. Reach the underlying object via `.bom` / `.component`. 
    See [`model.py`](siemens_standard_bom/model.py).
- Siemens-specific fields are NOT native CycloneDX: they're stored as `Property` entries keyed 
    `siemens:*` (constants at top of [`model.py`](siemens_standard_bom/model.py)) or as typed 
    `ExternalReference`s. Add a field by adding a constant + property getter/setter following existing 
    patterns.
- Reader supports BOTH v2 and v3 Standard BOM (see backward-compat branches in the `tools`/`authors` 
    getters); keep both working.
- Output is always CycloneDX JSON v1.6 (`JsonV1Dot6`). 
    [`StandardBomParser.save(..., with_dependencies=False)`](siemens_standard_bom/parser.py) re-reads 
    and strips `dependencies` from the file (prohibited in the 
    [`external` profile](https://sbom.siemens.io/v3/profiles.html)).

## Conventions

- [mypy](https://mypy.readthedocs.io/en/stable/) `strict = True`, `implicit_reexport = False`; 
- [flake8](https://flake8.pycqa.org/) max line length 140, max complexity 8, doctests checked.
- Requires Python >=3.10,<4.0 and [Poetry](https://python-poetry.org/) >= 2.0.
- Release: bump `version` in [`pyproject.toml`](pyproject.toml); pushing a `vX.Y.Z` tag publishes 
    to [PyPI](https://pypi.org/p/siemens-standard-bom) (see [`release.yml`](.github/workflows/release.yml)). 
- The self tool-entry version reads from installed package metadata, so `poetry install` 
    the package for it to report correctly.
