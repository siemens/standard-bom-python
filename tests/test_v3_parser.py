#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#

from datetime import datetime, timedelta, timezone

from cyclonedx.model.contact import OrganizationalContact
from packageurl import PackageURL

from siemens_standard_bom.model import SbomNature
from siemens_standard_bom.parser import StandardBomParser
from tests.abstract_sbom_compare import AbstractSbomComparingTestCase, read_timestamp


class SbomV3ParserTestCase(AbstractSbomComparingTestCase):
    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            StandardBomParser.parse("missing-file")

    def test_read_sunny_day(self) -> None:
        bom = StandardBomParser.parse("tests/v3/full-valid.cdx.json")
        self.assertIsNotNone(bom)

        self.assertIsNotNone(bom.tools)
        self.assertEqual(3, len(bom.tools))
        self.assertEqual(datetime.fromisoformat("2022-07-08T15:00:00+00:00"), bom.timestamp)

        self.assertEqual(1, len(bom.external_components))

        self.assertEqual(9, len(bom.components))
        commons_codec = next(comp for comp in bom.components if comp.name == "commons-codec")
        self.assertIsNotNone(commons_codec)
        self.assertEqual(commons_codec.name, "commons-codec")
        self.assertEqual(commons_codec.group, "commons-codec")
        self.assertEqual(commons_codec.version, "1.15")
        self.assertEqual(commons_codec.type, "library")
        self.assertEqual(commons_codec.purl,
                         PackageURL.from_string("pkg:maven/commons-codec/commons-codec@1.15?type=jar"))
        self.assertEqual(commons_codec.bom_ref.value, "pkg:maven/commons-codec/commons-codec@1.15?type=jar")
        self.assertEqual(commons_codec.description,
                         "The Apache Commons Codec package contains simple encoder and decoders for various formats"
                         " such as Base64 and Hexadecimal. In addition to these widely used encoders and decoders,"
                         " the codec package also maintains a collection of phonetic encoding utilities.")

        self.assertListEqual([
            OrganizationalContact(name="Daniel Rall of The Apache Software Foundation", email="dlr@finemaltcoding.com"),
            OrganizationalContact(name="David Graham of The Apache Software Foundation", email="dgraham@apache.org"),
            OrganizationalContact(name="Gary Gregory of The Apache Software Foundation", email="ggregory@apache.org"),
            OrganizationalContact(name="Henri Yandell of The Apache Software Foundation", email="bayard@apache.org"),
            OrganizationalContact(name="Jon S. Stevens of The Apache Software Foundation", email="jon@collab.net"),
            OrganizationalContact(name="Julius Davies of The Apache Software Foundation", email="julius@apache.org"),
            OrganizationalContact(name="Rob Tompkins of The Apache Software Foundation", email="chtompki@apache.org"),
            OrganizationalContact(name="Rodney Waldhoff of The Apache Software Foundation",
                                  email="rwaldhoff@apache.org"),
            OrganizationalContact(name="Scott Sanders of The Apache Software Foundation",
                                  email="sanders@totalsync.com"),
            OrganizationalContact(name="Thomas Neidhart of The Apache Software Foundation", email="tn@apache.org"),
            OrganizationalContact(name="Tim OBrien of The Apache Software Foundation", email="tobrien@apache.org")
        ], list(commons_codec.authors))

        self.assertEqual(commons_codec.copyright,
                         "Copyright 2002-2020 The Apache Software Foundation\n"
                         "Copyright (C) 2002 Kevin Atkinson (kevina@gnu.org)\n"
                         "Copyright (c) 2008 Alexander Beider & Stephen P. Morse.")

        self.assertIsNotNone(commons_codec.md5)
        self.assertIsNotNone(commons_codec.sha1)
        self.assertIsNotNone(commons_codec.sha256)
        self.assertIsNotNone(commons_codec.sha512)
        self.assertTrue(commons_codec.direct_dependency)
        self.assertEqual("commons-codec-1.15.jar", commons_codec.filename)
        self.assertEqual("Java", commons_codec.primary_language)
        assert commons_codec.third_party_notices is not None
        self.assertTrue(commons_codec.third_party_notices.startswith("Apache Commons Codec"))
        self.assertEqual("binaries/49d94806b6e3dc933dacbd8acb0fdbab8ebd1e5d/commons-codec-1.15.jar",
                         commons_codec.relative_path)

    def test_serial_number(self) -> None:
        input_filename = "tests/v3/serial-number.cdx.json"
        output_filename = "output/v3/serial-number.cdx.json"

        actual_bom, expected_bom = self.write_read_compare(input_filename, output_filename)
        self.assertEqual(actual_bom.serial_number, expected_bom.serial_number)

    def test_timestamps(self) -> None:
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

    def test_multiple_dependencies(self) -> None:
        input_filename = "tests/v3/multiple-dependencies.cdx.json"
        output_filename = "output/v3/multiple-dependencies.cdx.json"
        self.write_read_compare(input_filename, output_filename)

    def test_minimal_required(self) -> None:
        input_filename = "tests/v3/minimal-required.cdx.json"
        output_filename = "output/v3/minimal-required.cdx.json"

        actual_bom, expected_bom = self.write_read_compare(input_filename, output_filename)
        self.assertEqual(actual_bom.serial_number, expected_bom.serial_number)

    def test_single_dependency(self) -> None:
        input_filename = "tests/v3/single-dependency.cdx.json"
        output_filename = "output/v3/single-dependency.cdx.json"

        actual_bom, expected_bom = self.write_read_compare(input_filename, output_filename)
        self.assertEqual(actual_bom.serial_number, expected_bom.serial_number)

    def test_read_write_profile(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/test-profile.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.profile = "clearing"
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual("clearing", new_bom.profile)

    def test_read_write_vcs_clean(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/vcs-clean.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.vcs_clean = True
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertTrue(new_bom.vcs_clean)

    def test_read_write_vcs_revision(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/vcs-revision.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.vcs_revision = "123456"
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual("123456", new_bom.vcs_revision)

    def test_read_write_sbom_nature(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/sbom-nature.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.sbom_nature = SbomNature.SOURCE
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual(SbomNature.SOURCE, new_bom.sbom_nature)

    def test_read_write_internal(self) -> None:
        input_filename = "tests/v3/full-valid.cdx.json"
        output_filename = "output/v3/sbom-internal.cdx.json"

        bom = StandardBomParser.parse(input_filename)
        bom.internal = True
        StandardBomParser.save(bom, output_filename)
        new_bom = StandardBomParser.parse(output_filename)
        self.assertEqual(True, new_bom.internal)
