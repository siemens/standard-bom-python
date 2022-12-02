# Copyright (c) Siemens AG 2022 ALL RIGHTS RESERVED
import unittest

from cyclonedx.model import ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.component import Component, ComponentType

from standardbom.model import StandardBom, SbomComponent, ExternalComponent


class StandardBomTestCase(unittest.TestCase):
    def test_empty_components(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.components)
        self.assertEqual(0, len(sbom.components))

    def test_add_component(self):
        sbom = StandardBom()
        sbom.add_component(SbomComponent(Component(name="test.jar", component_type=ComponentType.LIBRARY)))
        self.assertEqual(1, len(sbom.components))
        self.assertEqual(sbom.components[0].name, "test.jar")
        self.assertEqual(sbom.components[0].type, ComponentType.LIBRARY)

    def test_empty_external_components(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.external_components)
        self.assertEqual(0, len(sbom.external_components))

    def test_add_external_component(self):
        sbom = StandardBom()
        sbom.add_external_component(ExternalComponent(ExternalReference(reference_type=ExternalReferenceType.WEBSITE,
                                                                        url=XsUri("sbom.siemens.io"))))
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, XsUri("sbom.siemens.io"))
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)


if __name__ == '__main__':
    unittest.main()
