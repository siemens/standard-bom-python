#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
#

import base64
import errno
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from uuid import UUID

from cyclonedx.model import AttachedText, ExternalReference, ExternalReferenceType, HashAlgorithm, HashType, Property, \
    Tool, XsUri
from cyclonedx.model.bom import Bom, BomMetaData
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.dependency import Dependency
from cyclonedx.model.license import DisjunctiveLicense, License, LicenseExpression
from cyclonedx.output.json import JsonV1Dot4
from cyclonedx.parser import BaseParser
from dateutil import parser as dateparser
from packageurl import PackageURL

from standardbom.model import StandardBom


def is_valid_serial_number(serial_number):
    return not (serial_number is None or "urn:uuid:None" == serial_number)


class SbomJsonParser(BaseParser):
    serial_number: Optional[UUID]
    metadata: Optional[BomMetaData]
    external_references: Optional[Iterable[ExternalReference]]

    def __init__(self, json_content: dict) -> None:
        super().__init__()
        self.metadata = read_metadata(json_content.get("metadata"))
        serial_number = json_content.get("serialNumber", None)
        self.serial_number = uuid.UUID(serial_number) \
            if is_valid_serial_number(serial_number) \
            else None
        components = json_content.get("components", [])
        for component_entry in components:
            component = read_component(component_entry)
            if component:
                self._components.append(component)
        self.external_references = read_external_references(json_content.get("externalReferences", None))
        self.dependencies = read_dependencies(json_content.get("dependencies"))


def read_dependencies(param: Optional[Any]) -> Optional[Iterable[Dependency]]:
    if param is None or not isinstance(param, Iterable):
        return None
    json_param: Iterable[Dict[Any, Any]] = param
    deps: list[Dependency] = []
    for dep_json in json_param:
        d = Dependency(ref=BomRef(dep_json.get('ref')))
        children: Optional[Iterable[str]] = dep_json.get('dependsOn')
        if children is not None:
            d.dependencies = [Dependency(ref=BomRef(c)) for c in children]
        deps.append(d)
    return deps


def read_tools(param: Iterable[dict]) -> Optional[Iterable[Tool]]:
    if param is None:
        return None
    tools = []
    for tool in param:
        tools.append(Tool(
            vendor=tool.get("vendor"),
            name=tool.get("name"),
            version=tool.get("version"),
            external_references=read_external_references(tool.get("externalReferences", None))
        ))
    return tools


def read_timestamp(param) -> Optional[datetime]:
    if param is None:
        return None
    try:
        timestamp = dateparser.isoparse(param)
        return timestamp
    except ValueError:
        return None


def read_url(param: Optional[str]) -> Optional[XsUri]:
    if param is None:
        return None
    return XsUri(uri=param)


def read_license(param: Optional[Any]) -> Optional[DisjunctiveLicense]:
    if param is None or not isinstance(param, Dict):
        return None
    param_json: Dict[str, Any] = param
    text = param_json.get("text", None)
    if isinstance(text, str):
        license_text = AttachedText(content=text)
    elif isinstance(text, dict) and 'content' in text:
        if 'encoding' in text and text['encoding'] == 'base64':
            license_text = AttachedText(content=base64.b64decode(text['content']).decode('utf-8'))
        else:
            license_text = AttachedText(content=text['content'])
    else:
        license_text = None
    return DisjunctiveLicense(
        id=param_json.get("id", None),
        name=param_json.get("name", None),
        text=license_text,
        url=read_url(param_json.get("url", None)),
    )


def read_licenses(param: Optional[Any]) -> Optional[Iterable[License]]:
    if param is None or not isinstance(param, Iterable):
        return None
    param_json: Iterable[Dict[Any, Any]] = param
    licenses: list[License] = []
    for entry in param_json:
        lic = read_license(entry.get("license", None))
        if lic:
            licenses.append(lic)
            continue
        exp = entry.get("expression", None)
        if isinstance(exp, str):
            licenses.append(LicenseExpression(exp))
    return licenses


def read_metadata(param) -> Optional[BomMetaData]:
    if param is None:
        return None
    licenses = read_licenses(param.get("licenses", None))
    metadata = BomMetaData(
        component=read_component(param.get("component", None)),
        properties=read_properties(param.get("properties", None)),
        licenses=licenses
    )
    if param.get("timestamp", None) is not None:
        timestamp = read_timestamp(param.get("timestamp"))
        if timestamp:
            metadata.timestamp = timestamp
    metadata.tools = read_tools(param.get("tools", None))
    return metadata


def read_hash_algorithm(param) -> HashAlgorithm:
    return HashAlgorithm(param)


def read_hashes(hashes_param: Optional[Any]) -> Optional[Iterable[HashType]]:
    if hashes_param is None or not isinstance(hashes_param, Iterable):
        return None
    hashes: Iterable[Dict[str, Any]] = hashes_param
    hash_types = []
    for entry in hashes:
        hash_types.append(HashType(
            alg=read_hash_algorithm(entry["alg"]),
            content=entry["content"]))
    return hash_types


def read_properties(values_param: Optional[Any]) -> Optional[Iterable[Property]]:
    if values_param is None or not isinstance(values_param, Iterable):
        return None
    values: Iterable[Dict[str, Any]] = values_param
    properties = []
    for entry in values:
        properties.append(Property(name=entry["name"], value=entry["value"]))
    return properties


def read_external_reference_type(value) -> ExternalReferenceType:
    return ExternalReferenceType(value)


def read_external_references(values: Optional[Any]) -> Optional[Iterable[ExternalReference]]:
    if values is None or not isinstance(values, Iterable):
        return None
    extrefs_json: Iterable[Dict[str, Any]] = values
    ex_refs = []
    for entry in extrefs_json:
        json_url = entry.get("url", None)
        if not isinstance(json_url, str):
            raise AttributeError('Mandatory field "url" not present in external reference')
        ex_refs.append(ExternalReference(
            type=read_external_reference_type(entry.get("type")),
            url=XsUri(json_url),
            comment=entry.get("comment"),
            hashes=read_hashes(entry.get("hashes", []))
        ))
    return ex_refs


def read_component(entry: Optional[Any]) -> Optional[Component]:
    if entry is None or not isinstance(entry, Dict):
        return None
    entry_dict: Dict[str, Any] = entry

    name: Optional[str] = entry_dict.get("name")
    if name is None:
        raise AttributeError('Mandatory field "name" not present in component')

    return Component(
        name=name,
        version=entry_dict.get("version"),
        group=entry_dict.get("group"),
        author=entry_dict.get("author"),
        description=entry_dict.get("description"),
        copyright=entry_dict.get("copyright"),
        purl=entry_dict.get("purl"),
        bom_ref=entry_dict.get("bom-ref"),
        type=read_component_type(entry_dict.get("type", None)),
        hashes=read_hashes(entry_dict.get("hashes", None)),
        properties=read_properties(entry_dict.get("properties", None)),
        external_references=read_external_references(entry_dict.get("externalReferences", None)),
        licenses=read_licenses(entry_dict.get("licenses", None))
    )


def read_component_type(type_str: Optional[Any]) -> ComponentType:
    if not isinstance(type_str, str):
        raise AttributeError('Mandatory field "type" not present in component')
    return ComponentType(type_str)


class StandardBomParser:
    @staticmethod
    def parse(filename: str) -> StandardBom:
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename)

        with open(filename, 'r', encoding='utf-8') as json_file:
            content = json.load(json_file)

            parser = SbomJsonParser(content)
            bom = Bom.from_parser(parser=parser)
            if parser.metadata:
                bom.metadata = parser.metadata
            bom.external_references = parser.external_references
            if parser.serial_number:
                bom.serial_number = parser.serial_number
            StandardBomParser.fix_purls(bom.metadata.component)
            if bom.components is not None:
                for comp in bom.components:
                    StandardBomParser.fix_purls(comp)
            if parser.dependencies is not None:
                bom.dependencies = parser.dependencies
            return StandardBom(bom)

    @staticmethod
    def fix_purls(comp: Optional[Component]) -> None:
        if comp is not None and isinstance(comp.purl, str):
            comp.purl = PackageURL.from_string(comp.purl)

    @staticmethod
    def reverse_keys(obj):
        if isinstance(obj, dict):
            return {k: StandardBomParser.reverse_keys(obj[k]) for k in reversed(obj)}
        elif isinstance(obj, list):
            return [StandardBomParser.reverse_keys(item) for item in obj]
        else:
            return obj

    @staticmethod
    def remove_dependencies_section(bom_file: str) -> None:
        content: Any
        with open(bom_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        if 'dependencies' in content:
            del content['dependencies']
        content = StandardBomParser.reverse_keys(content)
        with open(bom_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

    @staticmethod
    def save(sbom: StandardBom, output_filename: str) -> None:
        output_file = Path(output_filename)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        has_dependencies_section = len(sbom.cyclone_dx_sbom.dependencies) > 0
        writer = JsonV1Dot4(sbom.cyclone_dx_sbom)
        writer.output_to_file(filename=output_filename, allow_overwrite=True)

        # The 'save' action adds a dependencies section to the document. Remove it if we didn't have it before.
        if not has_dependencies_section:
            StandardBomParser.remove_dependencies_section(output_filename)
            if hasattr(sbom.cyclone_dx_sbom, 'dependencies'):
                sbom.cyclone_dx_sbom.dependencies.clear()
