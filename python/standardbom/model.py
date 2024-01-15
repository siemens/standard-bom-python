#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
#

from importlib.metadata import version
from typing import Iterable, List, Optional
from uuid import UUID

from cyclonedx.model import ExternalReference, ExternalReferenceType, HashAlgorithm, HashType, Property, XsUri
from cyclonedx.model.bom import Bom, BomMetaData, Tool
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.license import License, LicenseRepository
from packageurl import PackageURL

STANDARD_BOM_MODULE: str = 'standard-bom'

DIRECT_DEPENDENCY = "siemens:direct"
PRIMARY_LANGUAGE = "siemens:primaryLanguage"
THIRD_PARTY_NOTICES = "siemens:thirdPartyNotices"
LEGAL_REMARK = "siemens:legalRemark"
FILENAME = "siemens:filename"
PROFILE_KEY = "siemens:profile"

RELATIVE_PATH = "relativePath"
SOURCE_ARCHIVE = "source archive"
SOURCE_ARCHIVE_LOCAL = SOURCE_ARCHIVE + " (local copy)"
SOURCE_ARCHIVE_URL = SOURCE_ARCHIVE + " (download location)"


def is_source_archive(ex_ref: ExternalReference) -> bool:
    return ex_ref.type == ExternalReferenceType.DISTRIBUTION \
        and ex_ref.comment is not None \
        and ex_ref.comment.startswith(SOURCE_ARCHIVE)


def is_local_source_archive(ex_ref: ExternalReference) -> bool:
    return is_source_archive(ex_ref) \
        and ex_ref.comment == SOURCE_ARCHIVE_LOCAL


def is_remote_source_archive(ex_ref: ExternalReference) -> bool:
    return is_source_archive(ex_ref) \
        and ex_ref.comment == SOURCE_ARCHIVE_URL


def is_source_artifact(ex_ref: ExternalReference) -> bool:
    return is_source_archive(ex_ref) \
        and (is_remote_source_archive(ex_ref)
             or is_local_source_archive(ex_ref))


def is_tool_standardbom(tool: Tool) -> bool:
    return tool.vendor == 'Siemens AG' \
        and tool.name == 'standard-bom'


class SbomComponent:
    """
    Describes an entry in a standard-bom-compliant SBOM.
    """

    component: Component

    def __init__(self, component: Optional[Component] = None) -> None:
        if component is None:
            self.component = Component(name='INVALID')
        else:
            self.component = component

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
    def author(self) -> Optional[str]:
        return self.component.author

    @author.setter
    def author(self, value: str) -> None:
        self.component.author = value

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
    def licenses(self) -> List[License]:
        if self.component.licenses is None:
            self.component.licenses = LicenseRepository()
        return list(self.component.licenses)

    def add_license(self, lic: License) -> None:
        self.component.licenses.add(lic)

    @property
    def third_party_notices(self) -> Optional[str]:
        return self._get_custom_property(THIRD_PARTY_NOTICES)

    @third_party_notices.setter
    def third_party_notices(self, value: str) -> None:
        self._set_custom_property(THIRD_PARTY_NOTICES, value)

    @property
    def direct_dependency(self) -> bool:
        return self._get_custom_property(DIRECT_DEPENDENCY) in ["True", "true"]

    @direct_dependency.setter
    def direct_dependency(self, value: str) -> None:
        self._set_custom_property(DIRECT_DEPENDENCY, value)

    @property
    def primary_language(self) -> Optional[str]:
        return self._get_custom_property(PRIMARY_LANGUAGE)

    @primary_language.setter
    def primary_language(self, value: str) -> None:
        self._set_custom_property(PRIMARY_LANGUAGE, value)

    @property
    def legal_remark(self) -> Optional[str]:
        return self._get_custom_property(LEGAL_REMARK)

    @legal_remark.setter
    def legal_remark(self, value: str) -> None:
        self._set_custom_property(LEGAL_REMARK, value)

    @property
    def filename(self) -> Optional[str]:
        return self._get_custom_property(FILENAME)

    @filename.setter
    def filename(self, value: str) -> None:
        self._set_custom_property(FILENAME, value)

    def _get_custom_property(self, custom_property_key: str) -> Optional[str]:
        found = next(filter(lambda prop: prop.name == custom_property_key, self.component.properties), None)
        if found:
            return found.value
        return None

    def _set_custom_property(self, custom_property_key: str, value: str) -> None:
        found = next(filter(lambda prop: prop.name == custom_property_key, self.component.properties), None)
        if found:
            found.value = value
        else:
            self.component.properties.add(Property(name=custom_property_key, value=value))

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
        ex_ref = ExternalReference(type=ExternalReferenceType.DISTRIBUTION, comment=SOURCE_ARCHIVE_URL,
                                   url=XsUri(url), hashes=hashes)
        self.component.external_references.add(ex_ref)

    def _get_external_reference(self, ex_ref_type: ExternalReferenceType) -> Optional[ExternalReference]:
        return next(filter(lambda ex_ref: ex_ref.type == ex_ref_type if ex_ref else False,
                           self.component.external_references), None)

    def _set_external_reference(self, ex_ref_type: ExternalReferenceType, url: str) -> ExternalReference:
        reference = next(filter(lambda ex_ref: ex_ref.type == ex_ref_type, self.component.external_references), None)
        if not reference:
            reference = ExternalReference(type=ex_ref_type, url=XsUri(url))
            self.component.external_references.add(reference)
        return reference

    @property
    def external_components(self) -> List['ExternalComponent']:
        return list(map(lambda er: ExternalComponent(er), self.component.external_references))

    def add_external_component(self, external_component: 'ExternalComponent') -> None:
        self.component.external_references.add(external_component.external_ref)

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
                type=ExternalReferenceType.DISTRIBUTION,
                url=XsUri(download_url),
                comment=SOURCE_ARCHIVE_URL,
                hashes=hashes)
        elif local_file:
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.DISTRIBUTION,
                url=XsUri(local_file),
                comment=SOURCE_ARCHIVE_LOCAL,
                hashes=hashes)
        else:
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.DISTRIBUTION,
                url=XsUri('https://example.com'),
                comment=SOURCE_ARCHIVE,
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


class ExternalComponent:
    external_ref: ExternalReference

    def __init__(self, external_ref: Optional[ExternalReference] = None) -> None:
        if external_ref is None:
            self.external_ref = ExternalReference(
                type=ExternalReferenceType.OTHER,
                url=XsUri('https://example.com'))
        else:
            self.external_ref = external_ref

    @property
    def url(self) -> str:
        return str(self.external_ref.url)

    @url.setter
    def url(self, value: str) -> None:
        self.external_ref.url = XsUri(value)

    @property
    def type(self) -> ExternalReferenceType:
        return self.external_ref.type

    @type.setter
    def type(self, value: ExternalReferenceType) -> None:
        self.external_ref.type = value


class StandardBom:
    """
    Main DTO for the complete "Standard BOM" JSON structure.
    """

    cyclone_dx_sbom: Bom

    def __init__(self, cyclone_dx_sbom: Optional[Bom] = None) -> None:
        if cyclone_dx_sbom is None:
            self.cyclone_dx_sbom = Bom()
        else:
            self.cyclone_dx_sbom = cyclone_dx_sbom
            self.cyclone_dx_sbom.metadata.tools = \
                [tool for tool in self.cyclone_dx_sbom.metadata.tools if not is_tool_standardbom(tool)]
        self.cyclone_dx_sbom.metadata.tools.add(self.get_standard_bom_descriptor())

    @staticmethod
    def get_standard_bom_descriptor() -> Tool:
        result = Tool()
        result.vendor = 'Siemens AG'
        result.name = 'standard-bom'
        result.version = '2.4.0'
        website = ExternalReference(type=ExternalReferenceType.WEBSITE, url=XsUri('https://sbom.siemens.io/'))
        website.comment = f"Generated by the {STANDARD_BOM_MODULE} Python library v{version(STANDARD_BOM_MODULE)}"
        result.external_references = [website]
        return result

    @property
    def metadata(self) -> BomMetaData:
        return self.cyclone_dx_sbom.metadata

    @property
    def serial_number(self) -> UUID:
        return self.cyclone_dx_sbom.serial_number

    @property
    def components(self) -> List[SbomComponent]:
        return list(map(lambda c: SbomComponent(c), self.cyclone_dx_sbom.components))

    def add_component(self, sbom_component: SbomComponent) -> None:
        self.cyclone_dx_sbom.components.add(sbom_component.component)

    @property
    def external_components(self) -> List[ExternalComponent]:
        return list(map(lambda er: ExternalComponent(er), self.cyclone_dx_sbom.external_references))

    def add_external_component(self, external_component: ExternalComponent) -> None:
        self.cyclone_dx_sbom.external_references.add(external_component.external_ref)

    @property
    def profile(self) -> Optional[str]:
        prop = next(filter(lambda p: p.name == PROFILE_KEY,
                           self.cyclone_dx_sbom.metadata.properties), None)
        return prop.value if prop else None

    @profile.setter
    def profile(self, value: str) -> None:
        existing = next(filter(lambda p: p.name == PROFILE_KEY,
                               self.cyclone_dx_sbom.metadata.properties), None)
        if existing:
            if value:
                # update existing
                existing.value = value
            else:
                # remove existing
                self.cyclone_dx_sbom.metadata.properties.remove(existing)
        else:
            if value:
                prop = Property(name=PROFILE_KEY, value=value) if value else None
                self.cyclone_dx_sbom.metadata.properties.add(prop)
            else:
                # nothing to do
                pass
