# Copyright (c) Siemens AG 2019-2023 ALL RIGHTS RESERVED
import unittest

from cyclonedx.model import ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.component import Component, ComponentType

from standardbom.model import StandardBom, SbomComponent, ExternalComponent, is_tool_standardbom


class StandardBomTestCase(unittest.TestCase):
    def test_empty_components(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.components)
        self.assertEqual(0, len(sbom.components))

    def test_add_component(self):
        sbom = StandardBom()
        sbom.add_component(SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY)))
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
        sbom.add_external_component(ExternalComponent(ExternalReference(type=ExternalReferenceType.WEBSITE,
                                                                        url=XsUri("sbom.siemens.io"))))
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, XsUri("sbom.siemens.io"))
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_add_external_component2(self):
        excomp = ExternalComponent()
        excomp.type = ExternalReferenceType.WEBSITE
        excomp.url = 'https://sbom.siemens.io'
        sbom = StandardBom()
        sbom.add_external_component(excomp)
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, XsUri('https://sbom.siemens.io'))
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_tools_entry(self):
        sbom = StandardBom()
        self.assertEqual(2, len(sbom.metadata.tools))  # cyclonedx-python-lib and standard-bom
        [tool1, tool2] = sbom.metadata.tools
        actual_tool = tool1 if is_tool_standardbom(tool1) else tool2
        self.assertEqual('Siemens AG', actual_tool.vendor)
        self.assertEqual('standard-bom', actual_tool.name)
        self.assertEqual('2.4.0', actual_tool.version)
        self.assertIsNotNone(actual_tool.external_references)
        self.assertIsNotNone(1, len(actual_tool.external_references))

    def test_serial_number_provided(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.serial_number)

    def test_serial_number_unique(self):
        sbom = StandardBom()
        sbom2 = StandardBom()
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)

    def test_serial_number_unique_for_same_content(self):
        sbom = StandardBom()
        sbom.add_component(SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY)))
        sbom2 = StandardBom()
        sbom2.add_component(SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY)))
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)
