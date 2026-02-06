#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#
import enum
from datetime import datetime
from enum import Enum
from importlib.metadata import version as library_version
from typing import Iterable, List, Optional, Any
from uuid import UUID

from cyclonedx.model import ExternalReference, ExternalReferenceType, HashAlgorithm, HashType, Property, XsUri
from cyclonedx.model.bom import Bom
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType, ComponentScope
from cyclonedx.model.contact import OrganizationalEntity, OrganizationalContact
from cyclonedx.model.definition import Definitions, Standard
from cyclonedx.model.license import License, LicenseRepository
from cyclonedx.model.tool import Tool
from packageurl import PackageURL
from sortedcontainers import SortedSet

from siemens_standard_bom.immutable import ImmutableList

STANDARD_BOM_MODULE: str = 'siemens-standard-bom'

PROPERTY_DIRECT_DEPENDENCY = "siemens:direct"
PROPERTY_FILENAME = "siemens:filename"
PROPERTY_INTERNAL = "siemens:internal"
PROPERTY_LEGAL_REMARK = "siemens:legalRemark"
PROPERTY_PRIMARY_LANGUAGE = "siemens:primaryLanguage"
PROPERTY_PROFILE = "siemens:profile"
PROPERTY_THIRD_PARTY_NOTICES = "siemens:thirdPartyNotices"
PROPERTY_VCS_CLEAN = "siemens:vcsClean"
PROPERTY_VCS_REVISION = "siemens:vcsRevision"
PROPERTY_SBOM_NATURE = "siemens:sbomNature"

RELATIVE_PATH = "relativePath"
SOURCE_ARCHIVE_LOCAL = "source archive (local copy)"


def is_local_source_archive(ex_ref: ExternalReference) -> bool:
    return (ex_ref.type == ExternalReferenceType.DISTRIBUTION
            and ex_ref.comment is not None
            and ex_ref.comment == SOURCE_ARCHIVE_LOCAL)


def is_remote_source_archive(ex_ref: ExternalReference) -> bool:
    return ex_ref.type == ExternalReferenceType.SOURCE_DISTRIBUTION


def is_source_artifact(ex_ref: ExternalReference) -> bool:
    return (is_remote_source_archive(ex_ref)
            or is_local_source_archive(ex_ref))


class ExternalComponent:
    reference: ExternalReference

    def __init__(self, external_ref: Optional[ExternalReference] = None) -> None:
        if external_ref is None:
            self.reference = ExternalReference(
                type=ExternalReferenceType.OTHER,
                url=XsUri('https://example.com'))
        else:
            self.reference = external_ref

    @property
    def url(self) -> str:
        return str(self.reference.url)

    @url.setter
    def url(self, value: str) -> None:
        self.reference.url = XsUri(value)

    @property
    def type(self) -> ExternalReferenceType:
        return self.reference.type

    @type.setter
    def type(self, value: ExternalReferenceType) -> None:
        self.reference.type = value


class SbomComponent:
    """
    Describes an entry in a standard-bom-compliant SBOM.
    """

    component: Component

    def __init__(self, component: Component) -> None:
        self.component = component

    def __lt__(self, other: Any) -> bool:
        return self.component < other.component if isinstance(other, SbomComponent) else False

    @property
    def name(self) -> str:
        return self.component.name

    @name.setter
    def name(self, value: str) -> None:
        self.component.name = value

    @property
    def type(self) -> ComponentType:
        return self.component.type

    @type.setter
    def type(self, value: ComponentType) -> None:
        self.component.type = value

    @property
    def bom_ref(self) -> BomRef:
        return self.component.bom_ref

    @bom_ref.setter
    def bom_ref(self, value: BomRef) -> None:
        self.component._bom_ref = value

    @property
    def group(self) -> Optional[str]:
        return self.component.group

    @group.setter
    def group(self, value: str) -> None:
        self.component.group = value

    @property
    def version(self) -> Optional[str]:
        return self.component.version

    @version.setter
    def version(self, value: str) -> None:
        self.component.version = value

    @property
    def purl(self) -> Optional[PackageURL]:
        return self.component.purl

    @purl.setter
    def purl(self, value: PackageURL) -> None:
        self.component.purl = value

    @property
    def scope(self) -> Optional[ComponentScope]:
        return self.component.scope

    @scope.setter
    def scope(self, value: ComponentScope) -> None:
        self.component.scope = value

    @property
    def authors(self) -> ImmutableList[OrganizationalContact]:
        if self.component.authors is None:
            authors = ImmutableList[OrganizationalContact]()
        else:
            authors = ImmutableList[OrganizationalContact](self.component.authors)

        # Backward compatibility with v2
        if self.component.author is not None:
            authors_list = list(authors)
            authors_list.append(OrganizationalContact(name=self.component.author))
            authors = ImmutableList(authors_list)

        return authors

    @authors.setter
    def authors(self, authors: Iterable[OrganizationalContact]) -> None:
        self.component.authors = SortedSet(authors)

    def add_author(self, author: OrganizationalContact) -> None:
        if self.component.authors is None:
            self.component.authors = SortedSet()
        self.component.authors.add(author)

    @property
    def supplier(self) -> Optional[OrganizationalEntity]:
        return self.component.supplier

    @supplier.setter
    def supplier(self, value: OrganizationalEntity) -> None:
        self.component.supplier = value

    @property
    def description(self) -> Optional[str]:
        return self.component.description

    @description.setter
    def description(self, value: str) -> None:
        self.component.description = value

    @property
    def copyright(self) -> Optional[str]:
        return self.component.copyright

    @copyright.setter
    def copyright(self, value: str) -> None:
        self.component.copyright = value

    @property
    def cpe(self) -> Optional[str]:
        return self.component.cpe

    @cpe.setter
    def cpe(self, value: str) -> None:
        self.component.cpe = value

    @property
    def licenses(self) -> LicenseRepository:
        return self.component.licenses

    @licenses.setter
    def licenses(self, licenses: Iterable[License]) -> None:
        self.component.licenses = LicenseRepository(licenses)

    def add_license(self, lic: License) -> None:
        if self.licenses is None:
            self.licenses = []
        self.licenses.add(lic)

    @property
    def third_party_notices(self) -> Optional[str]:
        return self.get_custom_property(self.component, PROPERTY_THIRD_PARTY_NOTICES)

    @third_party_notices.setter
    def third_party_notices(self, value: str) -> None:
        self.set_custom_property(self.component, PROPERTY_THIRD_PARTY_NOTICES, value)

    @property
    def direct_dependency(self) -> bool:
        return self.get_custom_property(self.component, PROPERTY_DIRECT_DEPENDENCY) in ["True", "true"]

    @direct_dependency.setter
    def direct_dependency(self, value: str) -> None:
        self.set_custom_property(self.component, PROPERTY_DIRECT_DEPENDENCY, value)

    @property
    def internal(self) -> bool:
        return self.get_custom_property(self.component, PROPERTY_INTERNAL) in ["True", "true"]

    @internal.setter
    def internal(self, value: bool) -> None:
        self.set_custom_property(self.component, PROPERTY_INTERNAL, f"{value}")

    @property
    def primary_language(self) -> Optional[str]:
        return self.get_custom_property(self.component, PROPERTY_PRIMARY_LANGUAGE)

    @primary_language.setter
    def primary_language(self, value: str) -> None:
        self.set_custom_property(self.component, PROPERTY_PRIMARY_LANGUAGE, value)

    @property
    def legal_remark(self) -> Optional[str]:
        return self.get_custom_property(self.component, PROPERTY_LEGAL_REMARK)

    @legal_remark.setter
    def legal_remark(self, value: str) -> None:
        self.set_custom_property(self.component, PROPERTY_LEGAL_REMARK, value)

    @property
    def filename(self) -> Optional[str]:
        return self.get_custom_property(self.component, PROPERTY_FILENAME)

    @filename.setter
    def filename(self, value: str) -> None:
        self.set_custom_property(self.component, PROPERTY_FILENAME, value)

    @staticmethod
    def get_custom_property(component: Optional[Component], custom_property_key: str) -> Optional[str]:
        if component is not None and component.properties is not None and custom_property_key is not None:
            found = next(filter(lambda prop: prop.name == custom_property_key, component.properties), None)
            if found:
                return found.value
        return None

    @staticmethod
    def set_custom_property(component: Optional[Component], custom_property_key: str, value: str) -> None:
        if component is not None and component.properties is not None and custom_property_key is not None:
            found = next(filter(lambda prop: prop.name == custom_property_key, component.properties), None)
            if found:
                found.value = value
            else:
                component.properties.add(Property(name=custom_property_key, value=value))

    @property
    def website(self) -> Optional[str]:
        reference = self._get_external_reference(ExternalReferenceType.WEBSITE)
        return str(reference.url) if reference else None

    @website.setter
    def website(self, value: str) -> None:
        self._set_external_reference(ExternalReferenceType.WEBSITE, value)

    @property
    def repo_url(self) -> Optional[str]:
        reference = self._get_external_reference(ExternalReferenceType.VCS)
        return str(reference.url) if reference else None

    @repo_url.setter
    def repo_url(self, value: str) -> None:
        self._set_external_reference(ExternalReferenceType.VCS, value)

    @property
    def relative_path(self) -> Optional[str]:
        ref = next(filter(lambda er: er.type == ExternalReferenceType.DISTRIBUTION and er.comment == RELATIVE_PATH,
                          self.component.external_references), None)
        if ref:
            ref_str = str(ref.url)
            if ref_str.startswith("file:///"):
                return ref_str[len("file:///"):]
            if ref_str.startswith("file:"):
                return ref_str[len("file:"):]
            return ref_str
        return None

    @relative_path.setter
    def relative_path(self, value: str) -> None:
        reference = next(
            filter(lambda ex_ref: ex_ref.type == ExternalReferenceType.DISTRIBUTION and ex_ref.comment == RELATIVE_PATH,
                   self.component.external_references), None)
        if not reference:
            reference = ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                          url=XsUri(value),
                                          comment=RELATIVE_PATH)
            self.component.external_references.add(reference)
        else:
            reference.url = XsUri(value)

    @property
    def sources(self) -> List['SourceArtifact']:
        return list(map(lambda er: SourceArtifact(er),
                        filter(is_source_artifact,
                               self.component.external_references)))

    @property
    def local_sources(self) -> List['SourceArtifact']:
        return list(map(lambda er: SourceArtifact(er),
                        filter(is_local_source_archive,
                               self.component.external_references)))

    def add_local_source(self, url: str, hashes: Optional[Iterable[HashType]] = None) -> None:
        ex_ref = ExternalReference(type=ExternalReferenceType.DISTRIBUTION, comment=SOURCE_ARCHIVE_LOCAL,
                                   url=XsUri(url), hashes=hashes)
        self.component.external_references.add(ex_ref)

    @property
    def remote_sources(self) -> List['SourceArtifact']:
        return list(map(lambda er: SourceArtifact(er),
                        filter(is_remote_source_archive,
                               self.component.external_references)))

    def add_remote_source(self, url: str, hashes: Optional[Iterable[HashType]] = None) -> None:
        ex_ref = ExternalReference(type=ExternalReferenceType.SOURCE_DISTRIBUTION, url=XsUri(url), hashes=hashes)
        self.component.external_references.add(ex_ref)

    def _get_external_reference(self, ex_ref_type: ExternalReferenceType) -> Optional[ExternalReference]:
        external_reference = next(filter(lambda ex_ref: ex_ref is not None and ex_ref.type == ex_ref_type,
                                         self.component.external_references), None)
        return external_reference

    def _set_external_reference(self, ex_ref_type: ExternalReferenceType, url: str) -> ExternalReference:
        reference = next(filter(lambda ex_ref: ex_ref.type == ex_ref_type, self.component.external_references), None)
        if not reference:
            reference = ExternalReference(type=ex_ref_type, url=XsUri(url))
            self.component.external_references.add(reference)
        return reference

    @property
    def external_components(self) -> ImmutableList[ExternalComponent]:
        references = self.component.external_references
        return ImmutableList(*map(lambda er: ExternalComponent(er), references))

    def add_external_component(self, external: ExternalComponent | ExternalReference) -> None:
        self.component.external_references.add(external
                                               if isinstance(external, ExternalReference)
                                               else external.reference)

    @property
    def md5(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.MD5)

    @md5.setter
    def md5(self, value: str) -> None:
        self._set_hash(HashAlgorithm.MD5, value)

    @property
    def sha1(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_1)

    @sha1.setter
    def sha1(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_1, value)

    @property
    def sha256(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_256)

    @sha256.setter
    def sha256(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_256, value)

    @property
    def sha512(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_512)

    @sha512.setter
    def sha512(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_512, value)

    def _get_hash(self, algorithm: HashAlgorithm) -> Optional[str]:
        h = next(filter(lambda hash_type: hash_type.alg == algorithm, self.component.hashes), None)
        return h.content if h else None

    def _set_hash(self, algorithm: HashAlgorithm, value: str) -> None:
        h = next(filter(lambda hash_type: hash_type.alg == algorithm, self.component.hashes), None)
        if h:
            h.content = value
        else:
            self.component.hashes.add(HashType(alg=algorithm, content=value))


class SourceArtifact:
    external_ref: ExternalReference

    def __init__(self, external_ref: Optional[ExternalReference] = None,
                 download_url: Optional[str] = None, local_file: Optional[str] = None,
                 hashes: Optional[Iterable[HashType]] = None) -> None:
        if external_ref:
            if download_url or local_file or hashes:
                raise ValueError('external_ref must be the only argument')
            self.external_ref = external_ref
        elif download_url:
            if local_file:
                raise ValueError('Cannot specify both local_file and download_url')
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.SOURCE_DISTRIBUTION,
                url=XsUri(download_url),
                hashes=hashes)
        elif local_file:
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.DISTRIBUTION,
                url=XsUri(local_file),
                comment=SOURCE_ARCHIVE_LOCAL,
                hashes=hashes)
        else:
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.SOURCE_DISTRIBUTION,
                url=XsUri('https://example.com'),
                hashes=hashes)

    @property
    def type(self) -> ExternalReferenceType:
        return self.external_ref.type

    @type.setter
    def type(self, value: ExternalReferenceType) -> None:
        self.external_ref.type = value

    @property
    def url(self) -> Optional[str]:
        return str(self.external_ref.url) if self.external_ref.url else None

    @url.setter
    def url(self, value: str) -> None:
        self.external_ref.url = XsUri(value)

    @property
    def md5(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.MD5)

    @md5.setter
    def md5(self, value: str) -> None:
        self._set_hash(HashAlgorithm.MD5, value)

    @property
    def sha1(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_1)

    @sha1.setter
    def sha1(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_1, value)

    @property
    def sha256(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_256)

    @sha256.setter
    def sha256(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_256, value)

    @property
    def sha512(self) -> Optional[str]:
        return self._get_hash(HashAlgorithm.SHA_512)

    @sha512.setter
    def sha512(self, value: str) -> None:
        self._set_hash(HashAlgorithm.SHA_512, value)

    def _get_hash(self, algorithm: HashAlgorithm) -> Optional[str]:
        h = next(filter(lambda hash_type: hash_type.alg == algorithm, self.external_ref.hashes), None)
        return h.content if h else None

    def _set_hash(self, algorithm: HashAlgorithm, value: str) -> None:
        h = next(filter(lambda hash_type: hash_type.alg == algorithm, self.external_ref.hashes), None)
        if h:
            h.content = value
        else:
            self.external_ref.hashes.add(HashType(alg=algorithm, content=value))


class SbomNature(str, Enum):
    SOURCE = "source"
    BINARY = "binary"

    def __new__(cls, value: object, *args: Any, **kwargs: Any) -> 'SbomNature':
        if not isinstance(value, (str, enum.auto)):
            raise TypeError(
                f"Values of StrEnums must be strings: {value!r} is a {type(value)}"
            )
        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self) -> str:
        return str(self.value)


def is_valid_serial_number(serial_number: str | None) -> bool:
    return not (serial_number is None or "urn:uuid:None" == serial_number)


def is_standardbom_component_entry(component: Component) -> bool:
    return component.supplier is not None \
        and component.supplier.name == 'Siemens AG' \
        and component.name == STANDARD_BOM_MODULE


def is_standardbom_tool_entry(tool: Tool) -> bool:
    return tool.vendor == 'Siemens AG' \
        and tool.name == STANDARD_BOM_MODULE


class StandardBom:
    """
    Main DTO for the complete "Standard BOM" JSON structure.
    """

    bom: Bom

    def __init__(self, bom: Optional[Bom] = None) -> None:
        if bom is None:
            self.bom = Bom()
        else:
            self.bom = bom
        self._insert_standard_bom_tools_entry_if_missing()
        self._insert_standard_bom_definitions_entry_if_missing()
        self._set_supplier_if_missing()

    def _insert_standard_bom_tools_entry_if_missing(self) -> None:
        standard_bom_tools_entry: Tool | Component | None = None
        for comp in self.bom.metadata.tools.components:
            if is_standardbom_component_entry(comp):
                standard_bom_tools_entry = comp

        # checking tools entry for backward compatibility with v2
        if standard_bom_tools_entry is None:
            for tool in self.bom.metadata.tools.tools:
                if is_standardbom_tool_entry(tool):
                    standard_bom_tools_entry = tool

        if standard_bom_tools_entry is None:
            component = Component(
                name=STANDARD_BOM_MODULE,
                version=library_version(STANDARD_BOM_MODULE),
                supplier=OrganizationalEntity(name='Siemens AG'),
                external_references=[ExternalReference(type=ExternalReferenceType.WEBSITE,
                                                       url=XsUri('https://sbom.siemens.io/'))]
            )
            self.bom.metadata.tools.components.add(component)

    def _insert_standard_bom_definitions_entry_if_missing(self) -> None:
        definitions_entry = self.bom.definitions
        if (definitions_entry is None
            or definitions_entry.standards is None
            or not any((standard.name == 'Standard BOM'
                        and standard.owner == 'Siemens AG') for standard in definitions_entry.standards)):
            standard = Standard(
                bom_ref='standard-bom',
                name='Standard BOM',
                version='3.0.0',
                description='The Standard for Software Bills of Materials in Siemens',
                owner='Siemens AG',
                external_references=[
                    ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri('https://sbom.siemens.io/'))]
            )
            if definitions_entry is None:
                definitions_entry = Definitions(standards=[standard])
            else:
                definitions_entry.standards.add(standard)
            self.bom.definitions = definitions_entry

    def _set_supplier_if_missing(self) -> None:
        if not self.bom.metadata.supplier:
            self.bom.metadata.supplier = OrganizationalEntity(name='Siemens or its Affiliates')

    def _set_metadata_property(self, property_name: str, value: Optional[str | None]) -> None:
        existing = next(filter(lambda p: p.name == property_name,
                               self.bom.metadata.properties), None)
        if existing:
            if value:
                # update existing
                existing.value = value
            else:
                # remove existing
                self.bom.metadata.properties.remove(existing)
        else:
            if value:
                # add new
                prop = Property(name=property_name, value=value)
                self.bom.metadata.properties.add(prop)
            else:
                # nothing to do
                pass

    def _get_metadata_property(self, property_name: str) -> Optional[str]:
        prop = next(filter(lambda p: p.name == property_name,
                           self.bom.metadata.properties), None)
        return prop.value if prop else None

    @property
    def serial_number(self) -> UUID:
        return self.bom.serial_number

    @serial_number.setter
    def serial_number(self, serial_number: UUID) -> None:
        self.bom.serial_number = serial_number

    @property
    def version(self) -> int:
        return self.bom.version

    @version.setter
    def version(self, version: int) -> None:
        self.bom.version = version

    @property
    def components(self) -> ImmutableList[SbomComponent]:
        comps = self.bom.components
        sbom_comps = map(lambda c: SbomComponent(c), comps)
        return ImmutableList(*sbom_comps)

    @components.setter
    def components(self, components: Iterable[Component]) -> None:
        self.bom.components = SortedSet(components)

    def add_component(self, component: Component | SbomComponent) -> None:
        self.bom.components.add(component
                                if isinstance(component, Component)
                                else component.component)

    @property
    def external_components(self) -> ImmutableList[ExternalComponent]:
        references = self.bom.external_references
        return ImmutableList(*map(lambda er: ExternalComponent(er), references))

    def add_external_component(self, external: ExternalReference | ExternalComponent) -> None:
        self.bom.external_references.add(external
                                         if isinstance(external, ExternalReference)
                                         else external.reference)

    @property
    def profile(self) -> Optional[str]:
        return self._get_metadata_property(PROPERTY_PROFILE)

    @profile.setter
    def profile(self, value: Optional[str | None]) -> None:
        self._set_metadata_property(PROPERTY_PROFILE, value)

    @property
    def vcs_clean(self) -> bool:
        return SbomComponent.get_custom_property(self.bom.metadata.component, PROPERTY_VCS_CLEAN) in ["True", "true"]

    @vcs_clean.setter
    def vcs_clean(self, value: bool) -> None:
        SbomComponent.set_custom_property(self.bom.metadata.component, PROPERTY_VCS_CLEAN, f"{value}")

    @property
    def vcs_revision(self) -> Optional[str]:
        return SbomComponent.get_custom_property(self.bom.metadata.component, PROPERTY_VCS_REVISION)

    @vcs_revision.setter
    def vcs_revision(self, value: str) -> None:
        SbomComponent.set_custom_property(self.bom.metadata.component, PROPERTY_VCS_REVISION, value)

    @property
    def sbom_nature(self) -> Optional[SbomNature]:
        value = self._get_metadata_property(PROPERTY_SBOM_NATURE)
        return SbomNature(value) if value else None

    @sbom_nature.setter
    def sbom_nature(self, value: SbomNature) -> None:
        self._set_metadata_property(PROPERTY_SBOM_NATURE, str(value))

    @property
    def internal(self) -> bool:
        return SbomComponent.get_custom_property(self.bom.metadata.component, PROPERTY_INTERNAL) in ["True", "true"]

    @internal.setter
    def internal(self, value: bool) -> None:
        SbomComponent.set_custom_property(self.bom.metadata.component, PROPERTY_INTERNAL, f"{value}")

    @property
    def timestamp(self) -> datetime:
        return self.bom.metadata.timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime) -> None:
        self.bom.metadata.timestamp = timestamp

    @property
    def authors(self) -> SortedSet[OrganizationalContact]:
        return self.bom.metadata.authors

    @authors.setter
    def authors(self, authors: Iterable[OrganizationalContact]) -> None:
        self.bom.metadata.authors = SortedSet(authors)

    def add_author(self, author: OrganizationalContact) -> None:
        if self.bom.metadata.authors is None:
            self.bom.metadata.authors = SortedSet()
        self.bom.metadata.authors.add(author)

    @property
    def tools(self) -> ImmutableList[SbomComponent]:
        tools = self.bom.metadata.tools.components

        # checking tools entry for backward compatibility with v2
        tools_list = self.bom.metadata.tools.tools
        if tools_list is not None and len(tools_list) > 0:
            m = map(lambda t: Component(name=t.name if t.name else "(unknown tool)",
                                        version=t.version, supplier=OrganizationalEntity(name=t.vendor),
                                        external_references=t.external_references), tools_list)
            comps: SortedSet[Component] = SortedSet(m)
            tools = tools.union(comps)

        return ImmutableList(*map(lambda c: SbomComponent(c), tools))

    def add_tool(self, tool: Component | SbomComponent) -> None:
        self.bom.metadata.tools.components.add(tool
                                               if isinstance(tool, Component)
                                               else tool.component)

    @property
    def component(self) -> Optional[SbomComponent]:
        return SbomComponent(self.bom.metadata.component) if self.bom.metadata.component is not None else None

    @component.setter
    def component(self, component: Component | SbomComponent) -> None:
        self.bom.metadata.component = component.component \
            if isinstance(component, SbomComponent) \
            else component

    @property
    def supplier(self) -> Optional[OrganizationalEntity]:
        return self.bom.metadata.supplier

    @property
    def definitions(self) -> Optional[Definitions]:
        return self.bom.definitions

    @definitions.setter
    def definitions(self, definitions: Definitions) -> None:
        self.bom.definitions = definitions
