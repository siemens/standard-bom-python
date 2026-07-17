#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#

import errno
import json
import os
from pathlib import Path

from cyclonedx.model.bom import Bom
from cyclonedx.output.json import JsonV1Dot6

from siemens_standard_bom.model import StandardBom


class StandardBomParser:
    @staticmethod
    def parse(filename: str) -> StandardBom:
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename)

        with open(filename, 'r', encoding='utf-8') as json_file:
            json_content = json.loads(json_file.read())

            bom: Bom = Bom.from_json(data=json_content)  # type: ignore[attr-defined]
            return StandardBom(bom)

    @staticmethod
    def save(sbom: StandardBom, output_filename: str, indent: int = 4, with_dependencies: bool = True) -> None:
        output_file = Path(output_filename)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        output = StandardBomParser.serialize(sbom, indent=indent, with_dependencies=with_dependencies)

        output_file.write_text(output, encoding='utf-8')

    @staticmethod
    def serialize(sbom: StandardBom, indent: int = 4, with_dependencies: bool = True) -> str:
        writer = JsonV1Dot6(bom=sbom.bom)
        output = writer.output_as_string(indent=indent)

        if not with_dependencies:
            data = json.loads(output)
            data.pop('dependencies', None)
            output = json.dumps(data, indent=indent)

        return output
