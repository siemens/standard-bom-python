#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#
import json
from os import path

from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.license import LicenseExpression

from siemens_standard_bom.model import StandardBom, SbomComponent
from siemens_standard_bom.parser import StandardBomParser
from tests.abstract_sbom_compare import AbstractSbomComparingTestCase


class SbomV3ParserWriteTestCase(AbstractSbomComparingTestCase):

    def test_write_sunny_day(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/test-output.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_external(self) -> None:
        input_filename = "tests/v3/metadata-external.cdx.json"
        output_filename = "output/v3/metadata-external.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_extensive(self) -> None:
        input_filename = "tests/v3/metadata-extensive.cdx.json"
        output_filename = "output/v3/metadata-extensive.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_with_components_bom_ref(self) -> None:
        output_filename = "output/v3/without-components-bom-ref.cdx.json"

        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertIsNotNone(data["components"][0]["bom-ref"])

    def test_write_after_add_component(self) -> None:
        output_filename = "output/v3/after-add-component.cdx.json"

        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertEqual(data["components"][0]["name"], "test")
            self.assertEqual(data["components"][0]["version"], "1.0.0")

    def test_write_after_components_add_component(self) -> None:
        output_filename = "output/v3/after-components-add-component.cdx.json"

        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertEqual(data["components"][0]["name"], "test")
            self.assertEqual(data["components"][0]["version"], "1.0.0")

    def test_write_empty_sbom_without_dependencies(self) -> None:
        output_filename = "output/v3/without-dependencies.cdx.json"

        sbom = StandardBom()
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertNotIn("dependencies", data)

    def test_write_with_dependencies_after_adding_a_component(self) -> None:
        output_filename = "output/v3/with-dependencies-after-add-component.cdx.json"

        sbom = StandardBom()
        comp = Component(
            name="Dummy",
            version="0.0.1"
        )
        sbom.add_component(comp)
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertIn("dependencies", data)
            self.assertTrue(len(data["dependencies"]) == 1)

    def test_write_without_dependencies_after_adding_a_component(self) -> None:
        output_filename = "output/v3/without-dependencies-after-add-component.cdx.json"

        sbom = StandardBom()
        comp = Component(
            name="Dummy",
            version="0.0.1"
        )
        sbom.add_component(comp)
        StandardBomParser.save(sbom, output_filename, with_dependencies=False)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertNotIn("dependencies", data)

    def test_write_with_added_license(self) -> None:
        output_filename = "output/v3/with_added_license.json"

        sbom = StandardBom()
        comp = SbomComponent(Component(
            name="Dummy",
            version="0.0.1",
            type=ComponentType.LIBRARY,
        ))

        comp.add_license(LicenseExpression("MIT"))

        sbom.add_component(comp)
        StandardBomParser.save(sbom, output_filename, with_dependencies=False)

        self.assertTrue(path.exists(output_filename))
        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertEqual(data["components"][0]["name"], "Dummy")
            self.assertEqual(data["components"][0]["version"], "0.0.1")
            self.assertEqual(data["components"][0]["type"], ComponentType.LIBRARY)
            self.assertEqual(data["components"][0]["licenses"], [{'expression': 'MIT'}])

    def test_write_with_set_licenses(self) -> None:
        output_filename = "output/v3/with_set_licenses.json"

        sbom = StandardBom()
        comp = SbomComponent(Component(
            name="Dummy",
            version="0.0.1",
            type=ComponentType.LIBRARY,
        ))

        licenses = [LicenseExpression("MIT")]
        comp.licenses = licenses   # type: ignore[assignment] # this is a mypy issue

        sbom.add_component(comp)
        StandardBomParser.save(sbom, output_filename, with_dependencies=False)

        self.assertTrue(path.exists(output_filename))
        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertEqual(data["components"][0]["name"], "Dummy")
            self.assertEqual(data["components"][0]["version"], "0.0.1")
            self.assertEqual(data["components"][0]["type"], ComponentType.LIBRARY)
            self.assertEqual(data["components"][0]["licenses"], [{'expression': 'MIT'}])
