#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#

import unittest
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from cyclonedx.model.bom_ref import BomRef
from dateutil import parser as dateparser
from deepdiff import DeepDiff

from standardbom.model import StandardBom
from standardbom.parser import StandardBomParser

# excluding bom_ref values mainly from metadata.component.bom_ref
exclude_regex_paths = [
    r'.*dependencies.*\.[_]?ref\.[_]?value',
    r'.*metadata.*\.[_]?ref\.[_]?value',
    r'.*metadata.*\.[_]?bom_ref\.[_]?value',
    r'root.component.component\.[_]?bom_ref\.[_]?value',
    r'root.component\.[_]?bom_ref\.[_]?value',
]


class AbstractSbomComparingTestCase(ABC, unittest.TestCase):
    def write_read_compare(self, input_filename: str, output_filename: str) -> Tuple[StandardBom, StandardBom]:
        expected_bom = StandardBomParser.parse(input_filename)
        StandardBomParser.save(expected_bom, output_filename)
        self.assertTrue(Path(output_filename).is_file())
        actual_bom = StandardBomParser.parse(output_filename)

        self.assertEqual({}, DeepDiff(expected_bom.version, actual_bom.version))
        self.assertEqual({}, DeepDiff(expected_bom.serial_number, actual_bom.serial_number))
        self.assertEqual({}, DeepDiff(expected_bom.profile, actual_bom.profile))
        self.assertEqual({}, DeepDiff(expected_bom.sbom_nature, actual_bom.sbom_nature))
        self.assertEqual({}, DeepDiff(expected_bom.internal, actual_bom.internal))
        self.assertEqual({}, DeepDiff(expected_bom.timestamp, actual_bom.timestamp))
        self.assertEqual({}, DeepDiff(expected_bom.authors, actual_bom.authors))
        self.assertEqual({}, DeepDiff(expected_bom.supplier, actual_bom.supplier))

        self.assertEqual({}, DeepDiff(expected_bom.component, actual_bom.component, exclude_types=[BomRef]))
        self.assertEqual({}, DeepDiff(expected_bom.tools, actual_bom.tools))
        self.assertEqual({}, DeepDiff(expected_bom.components, actual_bom.components))
        self.assertEqual({}, DeepDiff(expected_bom.external_components, actual_bom.external_components))
        self.assertEqual({}, DeepDiff(expected_bom.bom, actual_bom.bom, exclude_regex_paths=exclude_regex_paths))
        self.assertEqual({}, DeepDiff(expected_bom, actual_bom, exclude_regex_paths=exclude_regex_paths))
        return actual_bom, expected_bom


def read_timestamp(param: str | None) -> Optional[datetime]:
    if param is None:
        return None
    try:
        timestamp = dateparser.isoparse(param)
        return timestamp
    except ValueError:
        return None
