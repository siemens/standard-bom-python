#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
#
import json
from os import path
from unittest import skip

from cyclonedx.model.component import Component

from standardbom.model import StandardBom
from standardbom.parser import StandardBomParser
from tests.abstract_sbom_compare import AbstractSbomComparingTestCase


class SbomV3ParserWriteTestCase(AbstractSbomComparingTestCase):

    def test_write_sunny_day(self):
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/test-output.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_external(self):
        input_filename = "tests/v3/metadata-external.cdx.json"
        output_filename = "output/v3/metadata-external.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_extensive(self):
        input_filename = "tests/v3/metadata-extensive.cdx.json"
        output_filename = "output/v3/metadata-extensive.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_without_dependencies(self):
        output_filename = "output/v3/without-dependencies.cdx.json"

        sbom = StandardBom()
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertNotIn("dependencies", data)

    def test_write_without_dependencies_with_component(self):
        output_filename = "output/v3/without-dependencies-with-component.cdx.json"

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
            self.assertNotIn("dependencies", data)

    def test_write_with_components_bom_ref(self):
        output_filename = "output/v3/without-components-bom-ref.cdx.json"

        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        StandardBomParser.save(sbom, output_filename)
        self.assertTrue(path.exists(output_filename))

        with open(output_filename, 'r') as file:
            data = json.load(file)
            self.assertIsNotNone(data["components"][0]["bom-ref"])
