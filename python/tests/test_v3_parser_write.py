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

