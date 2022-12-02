# Copyright (c) Siemens AG 2022 ALL RIGHTS RESERVED
import errno
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterable
from uuid import UUID

from cyclonedx.model import HashType, HashAlgorithm, Property, ExternalReference, ExternalReferenceType, Tool, \
    LicenseChoice, License, AttachedText, XsUri
from cyclonedx.model.bom import Bom, BomMetaData
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.output.json import JsonV1Dot4
from cyclonedx.parser import BaseParser
from dateutil import parser as dateparser

from standardbom.model import StandardBom


def is_valid_serial_number(serial_number):
    return not (serial_number is None or "urn:uuid:None" == serial_number)


class SbomJsonParser(BaseParser):
    serial_number: Optional[UUID]
    metadata: Optional[BomMetaData]
    external_references: Optional[Iterable[ExternalReference]]

    def __init__(self, json_content: dict):
        super().__init__()
        self.metadata = read_metadata(json_content.get("metadata"))
        serial_number = json_content.get("serialNumber", None)
        self.serial_number = uuid.UUID(serial_number) \
            if is_valid_serial_number(serial_number) \
            else None
        components = json_content.get("components", None)
        if components:
            for component_entry in components:
                component = read_component(component_entry)
                if component:
                    self._components.append(component)
        self.external_references = read_external_references(json_content.get("externalReferences", None))


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


def read_url(param: str) -> Optional[XsUri]:
    if param is None:
        return None
    return XsUri(uri=param)


def read_license(param: dict) -> Optional[License]:
    if param is None:
        return None
    text = param.get("text", None)
    license_text = AttachedText(content=text) if text else None
    return License(
        spdx_license_id=param.get("id", None),
        license_name=param.get("name", None),
        license_text=license_text,
        license_url=read_url(param.get("url", None)),
    )


def read_licenses(param: Iterable[dict]) -> Optional[Iterable[LicenseChoice]]:
    if param is None:
        return None
    licenses = []
    for entry in param:
        lic = read_license(entry.get("license", None))
        if lic:
            licenses.append(LicenseChoice(license_=lic))
            continue
        exp = entry.get("expression", None)
        if exp:
            licenses.append(LicenseChoice(license_expression=exp))
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


def read_hashes(hashes: Iterable[dict]) -> Optional[Iterable[HashType]]:
    if hashes is None:
        return None
    hash_types = []
    for entry in hashes:
        hash_types.append(HashType(
            algorithm=read_hash_algorithm(entry["alg"]),
            hash_value=entry["content"]))
    return hash_types


def read_properties(values: Iterable[dict]) -> Optional[Iterable[Property]]:
    if values is None:
        return None
    properties = []
    for entry in values:
        properties.append(Property(name=entry["name"], value=entry["value"]))
    return properties


def read_external_reference_type(value) -> ExternalReferenceType:
    return ExternalReferenceType(value)


def read_external_references(values: Iterable[dict]) -> Optional[Iterable[ExternalReference]]:
    if values is None:
        return None
    ex_refs = []
    for entry in values:
        ex_refs.append(ExternalReference(
            reference_type=read_external_reference_type(entry.get("type")),
            url=entry.get("url", None),
            comment=entry.get("comment"),
            hashes=read_hashes(entry.get("hashes", []))
        ))
    return ex_refs


def read_component(entry: dict) -> Optional[Component]:
    if entry is None:
        return None
    return Component(
        name=entry.get("name", None),
        version=entry.get("version"),
        group=entry.get("group"),
        author=entry.get("author"),
        description=entry.get("description"),
        copyright_=entry.get("copyright"),
        purl=entry.get("purl"),
        bom_ref=entry.get("bom-ref"),
        component_type=read_component_type(entry.get("type", None)),
        hashes=read_hashes(entry.get("hashes", None)),
        properties=read_properties(entry.get("properties", None)),
        external_references=read_external_references(entry.get("externalReferences", None)),
        licenses=read_licenses(entry.get("licenses", None))
    )


def read_component_type(type_str: str) -> ComponentType:
    return ComponentType(type_str)


class StandardBomParser:
    @staticmethod
    def parse(filename: str) -> StandardBom:
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename)

        with open(filename) as json_file:
            content = json.load(json_file)

            parser = SbomJsonParser(content)
            bom = Bom.from_parser(parser=parser)
            if parser.metadata:
                bom.metadata = parser.metadata
            bom.external_references = parser.external_references
            if parser.serial_number:
                bom.uuid = parser.serial_number
            return StandardBom(bom)

    @staticmethod
    def save(sbom: StandardBom, output_filename: str) -> None:
        output_file = Path(output_filename)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        writer = JsonV1Dot4(sbom.cyclone_dx_sbom)
        writer.output_to_file(filename=output_filename, allow_overwrite=True)
