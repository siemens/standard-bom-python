#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#

import errno
import json
import os
from pathlib import Path

from cyclonedx.model.bom import Bom
from cyclonedx.output.json import JsonV1Dot6

from standardbom.model import StandardBom


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

        writer = JsonV1Dot6(bom=sbom.bom)
        writer.output_to_file(filename=output_filename, allow_overwrite=True, indent=indent)

        if not with_dependencies:
            StandardBomParser._patch_to_remove_dependencies(output_filename, indent)

    @staticmethod
    def _patch_to_remove_dependencies(output_filename: str, indent: int = 4) -> None:
        with open(output_filename, 'r') as file:
            data = json.load(file)
            data.pop('dependencies', None)
        with open(output_filename, 'w') as file:
            json.dump(data, file, indent=indent)
