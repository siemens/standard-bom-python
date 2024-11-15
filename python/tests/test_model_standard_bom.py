# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
import datetime
import unittest
from importlib.metadata import version

from cyclonedx.model import ExternalReference, ExternalReferenceType, XsUri
from cyclonedx.model.component import ComponentType, Component
from cyclonedx.model.contact import OrganizationalContact
from cyclonedx.model.definition import Standard

from standardbom.model import StandardBom, SbomComponent, ExternalComponent, is_standardbom_component_entry


class StandardBomTestCase(unittest.TestCase):
    def test_empty_components(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom)
        self.assertIsNotNone(sbom.components)
        self.assertEqual(0, len(sbom.components))

    def test_add_component(self):
        sbom = StandardBom()
        sbom.add_component(Component(name="test.jar", type=ComponentType.LIBRARY))
        self.assertEqual(1, len(sbom.components))
        self.assertEqual(sbom.components[0].name, "test.jar")
        self.assertEqual(sbom.components[0].type, ComponentType.LIBRARY)

    def test_add_component_sbom_component(self):
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

    def test_add_external_component_external_reference(self):
        sbom = StandardBom()
        sbom.add_external_component(ExternalReference(type=ExternalReferenceType.WEBSITE,
                                                      url=XsUri("sbom.siemens.io")))
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, "sbom.siemens.io")
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_add_external_component(self):
        ext_comp = ExternalComponent()
        ext_comp.type = ExternalReferenceType.WEBSITE
        ext_comp.url = 'https://sbom.siemens.io'
        sbom = StandardBom()
        sbom.add_external_component(ext_comp)
        self.assertEqual(1, len(sbom.external_components))
        self.assertEqual(sbom.external_components[0].url, 'https://sbom.siemens.io')
        self.assertEqual(sbom.external_components[0].type, ExternalReferenceType.WEBSITE)

    def test_tools_entry(self):
        sbom = StandardBom()
        self.assertGreaterEqual(1, len(sbom.tools))  # standard-bom component is always present

        component: SbomComponent = next(filter(lambda c: is_standardbom_component_entry(c.component), sbom.tools))
        self.assertIsNotNone(component)
        self.assertEqual('Siemens AG', component.supplier.name)
        self.assertEqual('standard-bom', component.name)
        self.assertEqual(version('standard-bom'), component.version)
        self.assertEqual('https://sbom.siemens.io/', component.website)

    def test_tools_add_tool_and_get(self):
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        sbom.add_tool(tool)
        self.assertEqual(2, len(sbom.tools))

        test_tool: SbomComponent = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_tools_is_immutable(self):
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            sbom.tools.add(tool)

    def test_tools_is_iterable(self):
        sbom = StandardBom()
        tool = Component(name='test-tool', type=ComponentType.APPLICATION)
        sbom.add_tool(tool)
        # sbom.tools has tool and standard-bom, check existence of tool
        test_tool_exists = False
        for comp in sbom.tools:
            if comp.name == 'test-tool':
                test_tool_exists = True
        self.assertTrue(test_tool_exists)

    def test_add_tool(self):
        sbom = StandardBom()
        sbom.add_tool(Component(name='test-tool', type=ComponentType.APPLICATION))
        self.assertEqual(2, len(sbom.tools))

        test_tool: SbomComponent = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_add_tool_sbom_component(self):
        sbom = StandardBom()
        sbom.add_tool(SbomComponent(Component(name='test-tool', type=ComponentType.APPLICATION)))
        self.assertEqual(2, len(sbom.tools))

        test_tool: SbomComponent = next(filter(lambda x: x.name == 'test-tool', sbom.tools))
        self.assertIsNotNone(test_tool)
        self.assertEqual('test-tool', test_tool.name)
        self.assertEqual(ComponentType.APPLICATION, test_tool.type)

    def test_supplier_entry(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.supplier)
        self.assertEqual('Siemens or its Affiliates', sbom.supplier.name)

    def test_sbom_authors_is_initially_empty(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.authors)
        self.assertEqual(0, len(sbom.authors))

    def test_sbom_authors_is_set(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.authors)

        sbom.authors = [OrganizationalContact(name='John Doe')]
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

        sbom.add_author(OrganizationalContact(name='Jane Doe', phone='1234567890', email='someone@somewhere.com'))
        self.assertEqual(2, len(sbom.authors))

        new_contact: OrganizationalContact = next(filter(lambda x: x.name == 'Jane Doe', sbom.authors))
        self.assertIsNotNone(new_contact)
        self.assertEqual('Jane Doe', new_contact.name)
        self.assertEqual('1234567890', new_contact.phone)
        self.assertEqual('someone@somewhere.com', new_contact.email)

    def test_sbom_authors_add_and_get(self):
        sbom = StandardBom()
        author = OrganizationalContact(name='John Doe')
        sbom.authors.add(author)
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

    def test_sbom_authors_set_and_get(self):
        sbom = StandardBom()
        author = OrganizationalContact(name='John Doe')
        sbom.authors = [author]
        self.assertEqual(1, len(sbom.authors))
        self.assertEqual('John Doe', sbom.authors[0].name)

    def test_timestamp_provided(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.timestamp)
        self.assertGreaterEqual(datetime.datetime.now(tz=datetime.timezone.utc), sbom.timestamp)

    def test_timestamp_set(self):
        sbom = StandardBom()
        sbom.timestamp = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), sbom.timestamp)

    def test_serial_number_provided(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.serial_number)

    def test_serial_number_unique(self):
        sbom = StandardBom()
        sbom2 = StandardBom()
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)

    def test_serial_number_unique_for_same_content(self):
        sbom = StandardBom()
        sbom.add_component(Component(name='test.jar', type=ComponentType.LIBRARY))
        sbom2 = StandardBom()
        sbom2.add_component(Component(name='test.jar', type=ComponentType.LIBRARY))
        self.assertNotEqual(sbom.serial_number, sbom2.serial_number)

    def test_definitions_entry_is_provided(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.definitions)

    def test_definitions_standards_entry_is_provided(self):
        sbom = StandardBom()
        self.assertIsNotNone(sbom.definitions)
        self.assertIsNotNone(sbom.definitions.standards)
        self.assertEqual(1, len(sbom.definitions.standards))
        self.assertIsNotNone(sbom.definitions)
        self.assertIsNotNone(sbom.definitions.standards)
        self.assertGreaterEqual(1, len(sbom.definitions.standards))

        sbom_standard: Standard = next(filter(lambda x: x.name == 'Standard BOM' and x.owner == 'Siemens AG',
                                              sbom.definitions.standards))
        self.assertIsNotNone(sbom_standard)
        self.assertEqual('standard-bom', f'{sbom_standard.bom_ref}')
        self.assertEqual('Standard BOM', sbom_standard.name)
        self.assertEqual('3.0.0', sbom_standard.version)
        self.assertEqual('Siemens AG', sbom_standard.owner)
        self.assertIsNotNone(sbom_standard.external_references)
        self.assertEqual(1, len(sbom_standard.external_references))
        self.assertEqual('https://sbom.siemens.io/', f'{sbom_standard.external_references[0].url}')
        self.assertEqual(ExternalReferenceType.WEBSITE, sbom_standard.external_references[0].type)

    def test_sbom_components_is_immutable(self):
        sbom = StandardBom()
        component = SbomComponent(Component(name="test", version="1.0.0"))
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            sbom.components.add(component)

    def test_sbom_components_is_iterable(self):
        sbom = StandardBom()
        component = Component(name="test", version="1.0.0")
        sbom.add_component(component)
        for comp in sbom.components:
            self.assertEqual(comp.component, component)

    def test_sbom_external_components_is_immutable(self):
        sbom = StandardBom()
        ext_comp = ExternalComponent(
            ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri("sbom.siemens.io")))
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            sbom.external_components.add(ext_comp)

    def test_sbom_external_components_is_iterable(self):
        sbom = StandardBom()
        external = ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri("sbom.siemens.io"))
        sbom.add_external_component(external)
        for comp in sbom.external_components:
            self.assertEqual(comp.reference, external)
