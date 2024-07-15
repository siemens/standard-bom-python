#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
#

from datetime import datetime, timedelta, timezone

from packageurl import PackageURL

from standardbom.model import SbomComponent, SbomNature
from standardbom.parser import read_timestamp, StandardBomParser
from tests.abstract_sbom_compare import AbstractSbomComparingTestCase


class SbomParserTestCase(AbstractSbomComparingTestCase):
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            StandardBomParser.parse("missing-file")

    def test_read_sunny_day(self):
        bom = StandardBomParser.parse("tests/full-valid.cdx.json")
        self.assertIsNotNone(bom)

        self.assertIsNotNone(bom.metadata)
        self.assertIsNotNone(bom.metadata.tools)
        self.assertEqual(3, len(bom.metadata.tools))
        self.assertEqual(datetime.fromisoformat("2022-07-08T15:00:00+00:00"), bom.metadata.timestamp)

        self.assertEqual(1, len(bom.external_components))

        self.assertEqual(9, len(bom.components))
        commons_codec: SbomComponent = next(comp for comp in bom.components if comp.name == "commons-codec")
        self.assertIsNotNone(commons_codec)
        self.assertEqual(commons_codec.name, "commons-codec")
        self.assertEqual(commons_codec.group, "commons-codec")
        self.assertEqual(commons_codec.version, "1.13")
        self.assertEqual(commons_codec.type, "library")
        self.assertEqual(commons_codec.purl,
                         PackageURL.from_string("pkg:maven/commons-codec/commons-codec@1.13?type=jar"))
        self.assertEqual(commons_codec.bom_ref.value, "pkg:maven/commons-codec/commons-codec@1.13?type=jar")
        self.assertEqual(commons_codec.description,
                         "The Apache Commons Codec package contains simple encoder and decoders for various formats"
                         " such as Base64 and Hexadecimal. In addition to these widely used encoders and decoders,"
                         " the codec package also maintains a collection of phonetic encoding utilities.")
        self.assertEqual(commons_codec.author,
                         "Henri Yandell <bayard@apache.org>, Tim OBrien <tobrien@apache.org>,"
                         " Scott Sanders <sanders@totalsync.com>, Rodney Waldhoff <rwaldhoff@apache.org>,"
                         " Daniel Rall <dlr@finemaltcoding.com>, Jon S. Stevens <jon@collab.net>,"
                         " Gary Gregory <ggregory@apache.org>, David Graham <dgraham@apache.org>,"
                         " Julius Davies <julius@apache.org>, Thomas Neidhart <tn@apache.org>,"
                         " and Rob Tompkins <chtompki@apache.org> of The Apache Software Foundation")
        self.assertEqual(commons_codec.copyright,
                         "Copyright 2002-2019 The Apache Software Foundation\n"
                         "Copyright (C) 2002 Kevin Atkinson (kevina@gnu.org)\n"
                         "Copyright (c) 2008 Alexander Beider & Stephen P. Morse.")
        self.assertIsNotNone(commons_codec.md5)
        self.assertIsNotNone(commons_codec.sha1)
        self.assertIsNotNone(commons_codec.sha256)
        self.assertIsNotNone(commons_codec.sha512)
        self.assertTrue(commons_codec.direct_dependency)
        self.assertEqual("commons-codec-1.13.jar", commons_codec.filename)
        self.assertEqual("Java", commons_codec.primary_language)
        self.assertTrue(commons_codec.third_party_notices.startswith("Apache Commons Codec"))
        self.assertEqual("binaries/3f18e1aa31031d89db6f01ba05d501258ce69d2c/commons-codec-1.13.jar",
                         commons_codec.relative_path)

    def test_write_sunny_day(self):
        input_filename = "tests/full-valid.cdx.json"
        output_filename = "output/test-output.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_external(self):
        input_filename = "tests/metadata-external.cdx.json"
        output_filename = "output/metadata-external.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_write_metadata_extensive(self):
        input_filename = "tests/metadata-extensive.cdx.json"
        output_filename = "output/metadata-extensive.cdx.json"

        self.write_read_compare(input_filename, output_filename)

    def test_serial_number(self):
        input_filename = "tests/serial-number.cdx.json"
        output_filename = "output/serial-number.cdx.json"

        actual_bom, expected_bom = self.write_read_compare(input_filename, output_filename)
        self.assertEqual(actual_bom.serial_number, expected_bom.serial_number)

    def test_timestamps(self):
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 0, 0, timezone.utc), read_timestamp("2009-08-07T06:05Z"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone.utc), read_timestamp("2009-08-07T06:05:04Z"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone(timedelta(hours=1))),
                         read_timestamp("2009-08-07T06:05:04+01:00"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone(timedelta(hours=0))),
                         read_timestamp("2009-08-07T06:05:04+00:00"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone(timedelta(hours=0))),
                         read_timestamp("2009-08-07T06:05:04+00"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone(timedelta(hours=1))),
                         read_timestamp("2009-08-07T06:05:04+01"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 4, 0, timezone(timedelta(hours=4, minutes=30))),
                         read_timestamp("2009-08-07T06:05:04+04:30"))
        self.assertEqual(datetime(2009, 8, 7, 6, 5, 0, 0, timezone(timedelta(hours=4))),
                         read_timestamp("2009-08-07T06:05+04:00"))

    def test_multiple_dependencies(self):
        input_filename = "tests/multiple-dependencies.cdx.json"
        output_filename = "output/multiple-dependencies.cdx.json"
        self.write_read_compare(input_filename, output_filename)

    def test_minimal_required(self):
        input_filename = "tests/minimal-required.cdx.json"
        output_filename = "output/minimal-required.cdx.json"

        actual_bom, expected_bom = self.write_read_compare(input_filename, output_filename)
        self.assertEqual(actual_bom.serial_number, expected_bom.serial_number)

    def test_read_write_profile(self):
        input_filename = "tests/full-valid.cdx.json"
        output_filename = "output/test-profile.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.profile = "clearing"
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual("clearing", new_bom.profile)

    def test_read_write_vcs_clean(self):
        input_filename = "tests/full-valid.cdx.json"
        output_filename = "output/vcs-clean.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.vcs_clean = True
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertTrue(new_bom.vcs_clean)

    def test_read_write_vcs_revision(self):
        input_filename = "tests/full-valid.cdx.json"
        output_filename = "output/vcs-revision.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.vcs_revision = "123456"
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual("123456", new_bom.vcs_revision)

    def test_read_write_sbom_nature(self):
        input_filename = "tests/full-valid.cdx.json"
        output_filename = "output/sbom-nature.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.sbom_nature = "source"
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual(SbomNature.SOURCE, new_bom.sbom_nature)
