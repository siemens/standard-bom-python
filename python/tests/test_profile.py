# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
import unittest

from standardbom.model import StandardBom


class ProfilesTestCase(unittest.TestCase):
    def test_default_profile(self):
        sbom = StandardBom()
        self.assertIsNone(sbom.profile)

    def test_set_and_get_none_profile(self):
        sbom = StandardBom()
        sbom.profile = None
        self.assertIsNone(sbom.profile)

    def test_set_and_get_profile(self):
        sbom = StandardBom()
        sbom.profile = "external"
        self.assertEqual("external", sbom.profile)

    def test_set_and_get_any_profile_value(self):
        sbom = StandardBom()
        sbom.profile = "something"
        self.assertEqual("something", sbom.profile)

    def test_set_and_get_another_profile(self):
        sbom = StandardBom()
        sbom.profile = "clearing"
        self.assertEqual("clearing", sbom.profile)
        sbom.profile = "external"
        self.assertEqual("external", sbom.profile)


if __name__ == '__main__':
    unittest.main()
