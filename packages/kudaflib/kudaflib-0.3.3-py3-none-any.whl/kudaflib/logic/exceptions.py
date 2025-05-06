# Adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/exceptions/__init__.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

from typing import List


class UnregisteredUnitTypeError(Exception):
    ...


class ParseMetadataError(Exception):
    ...


class InvalidTemporalityType(Exception):
    ...


class InvalidIdentifierType(Exception):
    ...


class InvalidDatasetName(Exception):
    ...


class ValidationError(Exception):
    errors: List[str] = []

    def __init__(self, source: str, errors: List[str]):
        self.errors = errors
        super().__init__(f"Errors found while validating {source}")
