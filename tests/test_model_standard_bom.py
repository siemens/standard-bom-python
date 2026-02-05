# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
import datetime
import unittest
from importlib.metadata import version

from cyclonedx.model import ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import ComponentType, Component
from cyclonedx.model.contact import OrganizationalContact
from sortedcontainers import SortedSet

from siemens_standard_bom.model import StandardBom, SbomComponent, ExternalComponent, is_standardbom_component_entry


class StandardBomTestCase(unittest.TestCase):
    def test_empty_components(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.components)
        self.assertEqual(0, len(sbom.components))

    def test_add_component(self) -> None:
        sbom = StandardBom()
        sbom.add_component(Component(name="test.jar", type=ComponentType.LIBRARY))
        self.assertEqual(1, len(sbom.components))
        self.assertEqual(sbom.components[0].name, "test.jar")
        self.assertEqual(sbom.components[0].type, ComponentType.LIBRARY)

    def test_add_component_sbom_component(self) -> None:
        sbom = StandardBom()
        sbom.add_component(SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY)))
        self.assertEqual(1, len(sbom.components))
        self.assertEqual(sbom.components[0].name, "test.jar")
        self.assertEqual(sbom.components[0].type, ComponentType.LIBRARY)

    def test_empty_external_components(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.external_components)
        self.assertEqual(0, len(sbom.external_components))

    def test_add_external_component_external_reference(self) -> None:
        sbom = StandardBom()
        sbom.add_external_component(ExternalReference(type=ExternalReferenceType.WEBSITE,
                                                      url=XsUri("sbom.siemens.io")))
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, "sbom.siemens.io")
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_add_external_component(self) -> None:
        ext_comp = ExternalComponent()
        ext_comp.type = ExternalReferenceType.WEBSITE
        ext_comp.url = 'https://sbom.siemens.io'
        sbom = StandardBom()
        sbom.add_external_component(ext_comp)
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, 'https://sbom.siemens.io')
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_tools_entry(self) -> None:
        sbom = StandardBom()
        self.assertGreaterEqual(1, len(sbom.tools))  # standard-bom component is always present

        component = next(filter(lambda c: is_standardbom_component_entry(c.component), sbom.tools))
        assert component is not None
        self.assertEqual('siemens-standard-bom', component.name)
        self.assertEqual(version('siemens-standard-bom'), component.version)
        self.assertEqual('https://sbom.siemens.io/', component.website)
        assert component.supplier is not None
        self.assertEqual('Siemens AG', component.supplier.name)

    def test_tools_add_tool_and_get(self) -> None:
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        sbom.add_tool(tool)
        self.assertEqual(2, len(sbom.tools))

        test_tool = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_tools_is_immutable(self) -> None:
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        with self.assertRaises(AttributeError):
            sbom.tools.add(tool)  # type: ignore[attr-defined]

    def test_tools_is_iterable(self) -> None:
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        sbom.add_tool(tool)
        # sbom.tools has tool and standard-bom, check existence of tool
        test_tool_exists = False
        for comp in sbom.tools:
            if comp.name == 'test-tool':
                test_tool_exists = True
        self.assertTrue(test_tool_exists)

    def test_add_tool(self) -> None:
        sbom = StandardBom()
        sbom.add_tool(Component(name='test-tool', type=ComponentType.APPLICATION))
        self.assertEqual(2, len(sbom.tools))

        test_tool = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_add_tool_sbom_component(self) -> None:
        sbom = StandardBom()
        sbom.add_tool(SbomComponent(Component(name='test-tool', type=ComponentType.APPLICATION)))
        self.assertEqual(2, len(sbom.tools))

        test_tool = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_supplier_entry(self) -> None:
        sbom = StandardBom()
        assert sbom.supplier is not None
        self.assertEqual('Siemens or its Affiliates', sbom.supplier.name)

    def test_sbom_authors_is_initially_empty(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom.authors)
        self.assertEqual(0, len(sbom.authors))

    def test_sbom_authors_is_set(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom.authors)

        sbom.authors = SortedSet([OrganizationalContact(name='John Doe')])
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

        sbom.add_author(OrganizationalContact(name='Jane Doe', phone='1234567890', email='someone@somewhere.com'))
        self.assertEqual(2, len(sbom.authors))

        new_contact = next(filter(lambda x: x.name == 'Jane Doe', sbom.authors))
        self.assertIsNotNone(new_contact)
        self.assertEqual('Jane Doe', new_contact.name)
        self.assertEqual('1234567890', new_contact.phone)
        self.assertEqual('someone@somewhere.com', new_contact.email)

    def test_sbom_authors_add_and_get(self) -> None:
        sbom = StandardBom()
        author = OrganizationalContact(name='John Doe')
        sbom.authors.add(author)
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

    def test_sbom_authors_set_and_get(self) -> None:
        sbom = StandardBom()
        author = OrganizationalContact(name='John Doe')
        sbom.authors = SortedSet([author])
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

    def test_timestamp_provided(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom.timestamp)
        self.assertGreaterEqual(datetime.datetime.now(tz=datetime.timezone.utc), sbom.timestamp)

    def test_timestamp_set(self) -> None:
        sbom = StandardBom()
        sbom.timestamp = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), sbom.timestamp)

    def test_serial_number_provided(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom.serial_number)

    def test_serial_number_unique(self) -> None:
        sbom = StandardBom()
        sbom2 = StandardBom()
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)

    def test_serial_number_unique_for_same_content(self) -> None:
        sbom = StandardBom()
        sbom.add_component(Component(name='test.jar', type=ComponentType.LIBRARY))
        sbom2 = StandardBom()
        sbom2.add_component(Component(name='test.jar', type=ComponentType.LIBRARY))
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)

    def test_definitions_entry_is_provided(self) -> None:
        sbom = StandardBom()
        self.assertIsNotNone(sbom.definitions)

    def test_definitions_standards_entry_is_provided(self) -> None:
        sbom = StandardBom()
        assert sbom.definitions is not None
        self.assertIsNotNone(sbom.definitions.standards)
        self.assertEqual(1, len(sbom.definitions.standards))
        self.assertIsNotNone(sbom.definitions)
        self.assertIsNotNone(sbom.definitions.standards)
        self.assertGreaterEqual(1, len(sbom.definitions.standards))

        sbom_standard = next(filter(lambda x: x.name == 'Standard BOM' and x.owner == 'Siemens AG',
                                    sbom.definitions.standards), None)
        assert sbom_standard is not None
        self.assertEqual('standard-bom', f'{sbom_standard.bom_ref}')
        self.assertEqual('Standard BOM', sbom_standard.name)
        self.assertEqual('3.0.0', sbom_standard.version)
        self.assertEqual('Siemens AG', sbom_standard.owner)
        self.assertIsNotNone(sbom_standard.external_references)
        self.assertEqual(1, len(sbom_standard.external_references))
        self.assertEqual('https://sbom.siemens.io/', f'{sbom_standard.external_references[0].url}')
        self.assertEqual(ExternalReferenceType.WEBSITE, sbom_standard.external_references[0].type)

    def test_sbom_components_is_immutable(self) -> None:
        sbom = StandardBom()
        component = SbomComponent(Component(name="test", version="1.0.0"))
        with self.assertRaises(AttributeError):
            sbom.components.add(component)  # type: ignore[attr-defined]

    def test_sbom_components_is_iterable(self) -> None:
        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        for comp in sbom.components:
            self.assertEqual(comp.component, component)

    def test_sbom_external_components_is_immutable(self) -> None:
        sbom = StandardBom()
        ext_comp = ExternalComponent(
            ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri("sbom.siemens.io")))
        with self.assertRaises(AttributeError):
            sbom.external_components.add(ext_comp)  # type: ignore[attr-defined]

    def test_sbom_external_components_is_iterable(self) -> None:
        sbom = StandardBom()
        external = ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri("sbom.siemens.io"))
        sbom.add_external_component(external)
        for comp in sbom.external_components:
            self.assertEqual(comp.reference, external)

    def test_metadata_component_is_created_when_missing(self) -> None:
        bom = Bom()
        bom.metadata.component = None

        sbom = StandardBom(bom)
        sbom._insert_standard_bom_metadata_component_entry_if_missing()  # noqa: SLF001
        self.assertIsNotNone(sbom.bom.metadata.component)
        self.assertEqual('Unknown', sbom.bom.metadata.component.name)
        self.assertEqual('0.0.0', sbom.bom.metadata.component.version)
        self.assertEqual(ComponentType.APPLICATION, sbom.bom.metadata.component.type)

    def test_metadata_component_is_not_overwritten_when_exists(self) -> None:
        bom = Bom()
        existing_component = Component(
            name='MyApplication',
            version='1.2.3',
            type=ComponentType.APPLICATION
        )
        bom.metadata.component = existing_component
        
        sbom = StandardBom(bom)
        sbom._insert_standard_bom_metadata_component_entry_if_missing()  # noqa: SLF001
        self.assertIsNotNone(sbom.bom.metadata.component)
        self.assertEqual('MyApplication', sbom.bom.metadata.component.name)
        self.assertEqual('1.2.3', sbom.bom.metadata.component.version)
        self.assertEqual(ComponentType.APPLICATION, sbom.bom.metadata.component.type)

    def test_metadata_component_property_get_when_exists(self) -> None:
        bom = Bom()
        test_component = Component(
            name='TestApp',
            version='2.0.0',
            type=ComponentType.LIBRARY
        )
        bom.metadata.component = test_component
        
        sbom = StandardBom(bom)
        self.assertIsNotNone(sbom.component)
        self.assertEqual('TestApp', sbom.component.name)
        self.assertEqual('2.0.0', sbom.component.version)
        self.assertEqual(ComponentType.LIBRARY, sbom.component.type)

    def test_metadata_component_property_get_when_missing(self) -> None:
        bom = Bom()
        bom.metadata.component = None
        
        sbom = StandardBom(bom)
        self.assertIsNotNone(sbom.component)
        self.assertEqual('Unknown', sbom.component.name)
        self.assertEqual('0.0.0', sbom.component.version)

    def test_metadata_component_property_set(self) -> None:
        sbom = StandardBom()
        new_component = SbomComponent(Component(
            name='SetApp',
            version='3.0.0',
            type=ComponentType.APPLICATION
        ))

        sbom.component = new_component
        self.assertIsNotNone(sbom.component)
        self.assertEqual('SetApp', sbom.component.name)
        self.assertEqual('3.0.0', sbom.component.version)
        self.assertEqual(ComponentType.APPLICATION, sbom.component.type)
