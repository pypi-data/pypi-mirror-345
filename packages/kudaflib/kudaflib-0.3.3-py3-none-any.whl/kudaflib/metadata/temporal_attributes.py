# Adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/components/temporal_attributes.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway
from copy import deepcopy

from kudaflib.logic.exceptions import InvalidTemporalityType


DESCRIPTIONS = {
    "FIXED": {
        "START": {
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Start date for event",
                },
            ],        },
        "STOP": {
             "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Stoppdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Stop date for event",
                },
            ],
        },
    },
    "ACCUMULATED": {
        "START": {
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Start date for event",
                },
            ],        },
        "STOP": {
             "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Stoppdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Stop date for event",
                },
            ],
        },
    },
    "STATUS": {
        "START": {
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Start date for event",
                },
            ],        },
        "STOP": {
             "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Stoppdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Stop date for event",
                },
            ],
        },
    },
    "EVENT": {
        "START": {
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Start date for event",
                },
            ],        },
        "STOP": {
             "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
            "description": [
                {
                    "languageCode": "no",
                    "value": "Stoppdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Stop date for event",
                },
            ],
        },
    },
}

START_VARIABLE_DEFINITION = {
    "shortName": "START",
    "dataType": "DATE",
    "variableRole": "Attribute",
    "valueDomain": {
        "description": [
            {
                "languageCode": "no",
                "value": "Datostreng i et hvilket som helst gyldig ISO 8601-format",
            },
            {
                "languageCode": "en",
                "value": "Date string in any valid ISO 8601 format",
            }
        ]
    },
}
STOP_VARIABLE_DEFINITION = {
    "shortName": "STOP",
    "dataType": "DATE",
    "variableRole": "Attribute",
    "valueDomain": {
        "description": [
            {
                "languageCode": "no",
                "value": "Datostreng i et hvilket som helst gyldig ISO 8601-format",
            },
            {
                "languageCode": "en",
                "value": "Date string in any valid ISO 8601 format",
            }
        ]
    },
}


def generate_start_time_attribute(temporality_type: str):
    try:
        start_attribute = deepcopy(START_VARIABLE_DEFINITION)
        start_attribute.update(DESCRIPTIONS[temporality_type]["START"])
        return start_attribute
    except KeyError as e:
        print(f"Invalid temporality type: {temporality_type} - from Key Error: {e}")
        raise InvalidTemporalityType(temporality_type) from e


def generate_stop_time_attribute(temporality_type: str):
    try:
        stop_attribute = deepcopy(STOP_VARIABLE_DEFINITION)
        stop_attribute.update(DESCRIPTIONS[temporality_type]["STOP"])
        return stop_attribute
    except KeyError as e:
        print(f"Invalid temporality type: {temporality_type} - from Key Error: {e}")
        raise InvalidTemporalityType(temporality_type) from e
