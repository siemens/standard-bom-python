import unittest
from pathlib import Path

from deepdiff import DeepDiff

from standardbom.model import StandardBom
from standardbom.parser import StandardBomParser
from abc import ABC


class AbstractSbomComparingTestCase(ABC, unittest.TestCase):

    def write_read_compare(self, input_filename, output_filename) -> (StandardBom, StandardBom):
        expected_bom = StandardBomParser.parse(input_filename)
        StandardBomParser.save(expected_bom, output_filename)
        self.assertTrue(Path(output_filename).is_file())
        actual_bom = StandardBomParser.parse(output_filename)
        self.assertEqual({}, DeepDiff(expected_bom.metadata.licenses, actual_bom.metadata.licenses))
        self.assertEqual({}, DeepDiff(expected_bom.metadata.properties, actual_bom.metadata.properties))
        self.assertEqual({}, DeepDiff(expected_bom.metadata, actual_bom.metadata))
        self.assertEqual({}, DeepDiff(expected_bom.components, actual_bom.components))
        self.assertEqual({}, DeepDiff(expected_bom.external_components, actual_bom.external_components))
        erg = DeepDiff(expected_bom, actual_bom, ignore_order=True, report_repetition=True, exclude_paths=[
            'root.cyclone_dx_sbom._serial_number',
            'root.cyclone_dx_sbom.serial_number',
            'root.serial_number',
            'root.cyclone_dx_sbom.uuid'],
                       exclude_regex_paths='\\._')
        self.assertEqual({}, erg)
        return actual_bom, expected_bom
