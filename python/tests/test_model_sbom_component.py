# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
import unittest

from cyclonedx.model import AttachedText, ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.license import DisjunctiveLicense
from packageurl import PackageURL

from standardbom.model import ExternalComponent, SbomComponent


class SBomComponentTestCase(unittest.TestCase):

    def test_construct(self):
        component = SbomComponent()
        self.assertEqual(ComponentType.LIBRARY, component.type)
        self.assertEqual("INVALID", component.name)
        self.assertIsNotNone(component.bom_ref)
        self.assertIsNone(component.group)
        self.assertIsNone(component.version)
        self.assertIsNone(component.purl)
        self.assertIsNone(component.author)
        self.assertIsNone(component.description)
        self.assertIsNone(component.copyright)
        self.assertIsNone(component.cpe)

    def test_direct_fields(self):
        component = SbomComponent(Component(name="test"))
        self.assertEqual("test", component.name)
        self.assertEqual(ComponentType.LIBRARY, component.type)
        self.assertIsNotNone(component.bom_ref)
        self.assertIsNone(component.group)
        self.assertIsNone(component.version)
        self.assertIsNone(component.purl)
        self.assertIsNone(component.author)
        self.assertIsNone(component.description)
        self.assertIsNone(component.copyright)
        self.assertIsNone(component.cpe)

    def test_property_setters(self):
        component = SbomComponent(Component(name="test"))

        component.name = "42"
        self.assertEqual("42", component.name)

        component.type = ComponentType.APPLICATION
        self.assertEqual(ComponentType.APPLICATION, component.type)

        component.bom_ref = BomRef(value="test-ref")
        self.assertEqual("test-ref", component.bom_ref.value)

        component.group = "test-group"
        self.assertEqual("test-group", component.group)

        component.version = "42.42"
        self.assertEqual("42.42", component.version)

        component.purl = PackageURL(type="generic", name="foo.zip")
        self.assertEqual("foo.zip", component.purl.name)

        component.author = "Lex Luthor"
        self.assertEqual("Lex Luthor", component.author)

        component.description = "evil unicorn powder"
        self.assertEqual("evil unicorn powder", component.description)

        component.copyright = "2199 (c) Acme Inc."
        self.assertEqual("2199 (c) Acme Inc.", component.copyright)

        component.cpe = "cpe:2.3:a:evil_corp:mars_explorer:1.2.3:beta:*:*:*:*:*:*"
        self.assertEqual("cpe:2.3:a:evil_corp:mars_explorer:1.2.3:beta:*:*:*:*:*:*", component.cpe)

    def test_licenses(self):
        component = SbomComponent()
        self.assertListEqual(list(), component.licenses)

        lic = DisjunctiveLicense(name="test",
                                 text=AttachedText(content="test license"),
                                 url=XsUri("test-uri"))
        component.add_license(lic)
        self.assertListEqual([lic], component.licenses)

    def test_third_party_notices(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.third_party_notices)

        component.third_party_notices = "test123"
        self.assertEqual("test123", component.third_party_notices)

    def test_direct_dependency(self):
        component = SbomComponent(Component(name="test"))
        self.assertFalse(component.direct_dependency)

        component.direct_dependency = "true"
        self.assertTrue(component.direct_dependency)

        component.direct_dependency = "True"
        self.assertTrue(component.direct_dependency)

        component.direct_dependency = "False"
        self.assertFalse(component.direct_dependency)

        component.direct_dependency = "something"
        self.assertFalse(component.direct_dependency)

    def test_internal(self):
        component = SbomComponent(Component(name="test"))
        self.assertFalse(component.internal)

        component.internal = "true"
        self.assertTrue(component.internal)

        component.internal = "True"
        self.assertTrue(component.internal)

        component.internal = "False"
        self.assertFalse(component.internal)

        component.internal = "something"
        self.assertFalse(component.internal)

    def test_primary_language(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.primary_language)

        component.primary_language = "test123"
        self.assertEqual("test123", component.primary_language)

    def test_legal_remark(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.legal_remark)

        component.legal_remark = "test123"
        self.assertEqual("test123", component.legal_remark)

    def test_filename(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.filename)

        component.filename = "test123"
        self.assertEqual("test123", component.filename)

    def test_website(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.website)

        component.website = "test123"
        self.assertEqual("test123", component.website)

    def test_repo_url(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.repo_url)

        component.repo_url = "test123"
        self.assertEqual("test123", component.repo_url)

    def test_relative_path(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.relative_path)

        component.relative_path = "test123"
        self.assertEqual("test123", component.relative_path)

        component.relative_path = "file:changed"
        self.assertEqual("changed", component.relative_path)

    def test_md5(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.md5)

        component.md5 = "test123"
        self.assertEqual("test123", component.md5)
        component.md5 = "changed"
        self.assertEqual("changed", component.md5)

    def test_sha1(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha1)

        component.sha1 = "test123"
        self.assertEqual("test123", component.sha1)
        component.sha1 = "changed"
        self.assertEqual("changed", component.sha1)

    def test_sha256(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha256)

        component.sha256 = "test123"
        self.assertEqual("test123", component.sha256)
        component.sha256 = "changed"
        self.assertEqual("changed", component.sha256)

    def test_sha512(self):
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha512)

        component.sha512 = "test123"
        self.assertEqual("test123", component.sha512)
        component.sha512 = "changed"
        self.assertEqual("changed", component.sha512)

    def test_add_get_external_components(self):
        component = SbomComponent(Component(name="test"))
        component.add_external_component(ExternalComponent(ExternalReference(
            type=ExternalReferenceType.BOM,
            url=XsUri("test")
        )))
        self.assertEqual(1, len(component.external_components))
        self.assertEqual(ExternalReferenceType.BOM, component.external_components[0].external_ref.type)


if __name__ == '__main__':
    unittest.main()
