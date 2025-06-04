# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT

import unittest

from cyclonedx.model import AttachedText, ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.component import ComponentType, Component
from cyclonedx.model.contact import OrganizationalContact
from cyclonedx.model.license import DisjunctiveLicense
from packageurl import PackageURL

from siemens_standard_bom.model import ExternalComponent, SbomComponent


class SBomComponentTestCase(unittest.TestCase):

    def test_construct_default_from_component(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertEqual(ComponentType.LIBRARY, component.type)
        self.assertEqual("test", component.name)
        self.assertIsNotNone(component.bom_ref)
        self.assertIsNone(component.group)
        self.assertIsNone(component.version)
        self.assertIsNone(component.purl)
        self.assertIsNotNone(component.authors)
        self.assertEqual(0, len(component.authors))
        self.assertIsNone(component.description)
        self.assertIsNone(component.copyright)
        self.assertIsNone(component.cpe)

    def test_direct_fields(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertEqual("test", component.name)
        self.assertEqual(ComponentType.LIBRARY, component.type)
        self.assertIsNotNone(component.bom_ref)
        self.assertIsNone(component.group)
        self.assertIsNone(component.version)
        self.assertIsNone(component.purl)
        self.assertIsNotNone(component.authors)
        self.assertEqual(0, len(component.authors))
        self.assertIsNone(component.description)
        self.assertIsNone(component.copyright)
        self.assertIsNone(component.cpe)

    def test_property_setters(self) -> None:
        component = SbomComponent(Component(name="test"))

        component.name = "42"
        self.assertEqual("42", component.name)

        component.type = ComponentType.APPLICATION
        self.assertEqual(ComponentType.APPLICATION, component.type)

        component.group = "test-group"
        self.assertEqual("test-group", component.group)

        component.version = "42.42"
        self.assertEqual("42.42", component.version)

        component.purl = PackageURL(type="generic", name="foo.zip")
        if component.purl is not None:
            self.assertEqual("foo.zip", component.purl.name)
        else:
            self.fail("component.purl should not be None")

        component.add_author(OrganizationalContact(name="Lex Luthor"))
        self.assertEqual("Lex Luthor", component.authors[0].name)

        component.description = "evil unicorn powder"
        self.assertEqual("evil unicorn powder", component.description)

        component.copyright = "2199 (c) Acme Inc."
        self.assertEqual("2199 (c) Acme Inc.", component.copyright)

        component.cpe = "cpe:2.3:a:evil_corp:mars_explorer:1.2.3:beta:*:*:*:*:*:*"
        self.assertEqual("cpe:2.3:a:evil_corp:mars_explorer:1.2.3:beta:*:*:*:*:*:*", component.cpe)

    def test_licenses(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertEqual(0, len(component.licenses))

        lic = DisjunctiveLicense(name="test",
                                 text=AttachedText(content="test license"),
                                 url=XsUri("test-uri"))
        component.add_license(lic)
        self.assertListEqual([lic], list(component.licenses))

    def test_third_party_notices(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.third_party_notices)

        component.third_party_notices = "test123"
        self.assertEqual("test123", component.third_party_notices)

    def test_direct_dependency(self) -> None:
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

    def test_internal(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertFalse(component.internal)

        component.internal = "true"  # type: ignore[assignment]
        self.assertTrue(component.internal)

        component.internal = "True"  # type: ignore[assignment]
        self.assertTrue(component.internal)

        component.internal = "False"  # type: ignore[assignment]
        self.assertFalse(component.internal)

        component.internal = "something"  # type: ignore[assignment]
        self.assertFalse(component.internal)

    def test_primary_language(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.primary_language)

        component.primary_language = "test123"
        self.assertEqual("test123", component.primary_language)

    def test_legal_remark(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.legal_remark)

        component.legal_remark = "test123"
        self.assertEqual("test123", component.legal_remark)

    def test_filename(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.filename)

        component.filename = "test123"
        self.assertEqual("test123", component.filename)

    def test_website(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.website)

        component.website = "test123"
        self.assertEqual("test123", component.website)

    def test_repo_url(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.repo_url)

        component.repo_url = "test123"
        self.assertEqual("test123", component.repo_url)

    def test_relative_path(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.relative_path)

        component.relative_path = "test123"
        self.assertEqual("test123", component.relative_path)

        component.relative_path = "file:changed"
        self.assertEqual("changed", component.relative_path)

    def test_md5(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.md5)

        component.md5 = "test123"
        self.assertEqual("test123", component.md5)
        component.md5 = "changed"
        self.assertEqual("changed", component.md5)

    def test_sha1(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha1)

        component.sha1 = "test123"
        self.assertEqual("test123", component.sha1)
        component.sha1 = "changed"
        self.assertEqual("changed", component.sha1)

    def test_sha256(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha256)

        component.sha256 = "test123"
        self.assertEqual("test123", component.sha256)
        component.sha256 = "changed"
        self.assertEqual("changed", component.sha256)

    def test_sha512(self) -> None:
        component = SbomComponent(Component(name="test"))
        self.assertIsNone(component.sha512)

        component.sha512 = "test123"
        self.assertEqual("test123", component.sha512)
        component.sha512 = "changed"
        self.assertEqual("changed", component.sha512)

    def test_add_external_component_external_reference(self) -> None:
        component = SbomComponent(Component(name="test"))
        component.add_external_component(ExternalComponent(ExternalReference(
            type=ExternalReferenceType.BOM,
            url=XsUri("test")
        )))
        self.assertEqual(1, len(component.external_components))
        self.assertEqual(ExternalReferenceType.BOM, component.external_components[0].reference.type)

    def test_add_external_component(self) -> None:
        component = SbomComponent(Component(name="test"))
        component.add_external_component(ExternalReference(
            type=ExternalReferenceType.BOM,
            url=XsUri("test")
        ))
        self.assertEqual(1, len(component.external_components))
        self.assertEqual(ExternalReferenceType.BOM, component.external_components[0].reference.type)

    def test_external_components_are_immutable(self) -> None:
        component = SbomComponent(Component(name="test"))
        reference = ExternalReference(
            type=ExternalReferenceType.BOM,
            url=XsUri("test")
        )
        with self.assertRaises(AttributeError):
            component.external_components.add(reference)  # type: ignore[attr-defined]

    def test_external_components_are_iterable(self) -> None:
        component = SbomComponent(Component(name="test"))
        e = ExternalReference(
            type=ExternalReferenceType.BOM,
            url=XsUri("test")
        )
        component.add_external_component(e)
        for external_comp in component.external_components:
            self.assertEqual(e, external_comp.reference)


if __name__ == '__main__':
    unittest.main()
