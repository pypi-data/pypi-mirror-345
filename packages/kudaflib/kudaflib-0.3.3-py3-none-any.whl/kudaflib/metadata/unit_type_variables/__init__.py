# Adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/components/unit_type_variables/__init__.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

from enum import Enum
from copy import deepcopy
from pathlib import Path

from kudaflib.logic.exceptions import InvalidIdentifierType
from kudaflib.logic.utils import load_json


GLOBAL_UNIT_TYPES_DIR = Path(__file__).parent
GLOBAL_UNIT_TYPES = {
    "KOMMUNE": load_json(GLOBAL_UNIT_TYPES_DIR / "KOMMUNE.json"),             # KUDAF added
    "FYLKE": load_json(GLOBAL_UNIT_TYPES_DIR / "FYLKE.json"),                 # KUDAF added
    "FYLKESKOMMUNE": load_json(GLOBAL_UNIT_TYPES_DIR / "FYLKESKOMMUNE.json"), # KUDAF added
    "PERSON": load_json(GLOBAL_UNIT_TYPES_DIR / "PERSON.json"),
    "ORGANISASJON": load_json(GLOBAL_UNIT_TYPES_DIR / "ORGANISASJON.json"),
}


def get(unit_type: str):
    try:
        return deepcopy(GLOBAL_UNIT_TYPES[unit_type])
    except KeyError as e:
        raise InvalidIdentifierType(unit_type) from e
