from enum import Enum
from pydantic import BaseModel


class TemporalityType(str, Enum):
    FIXED = "FIXED"
    STATUS = "STATUS"
    ACCUMULATED = "ACCUMULATED"
    EVENT = "EVENT"


class DataType(str, Enum):
    STRING = "STRING"
    LONG = "LONG"
    DATE = "DATE"
    DOUBLE = "DOUBLE"
    BOOL = "BOOL"


class SensitivityLevel(str, Enum):
    PUBLIC = "PUBLIC"
    NONPUBLIC = "NONPUBLIC"


class LanguageCode(str, Enum):
    no = "no"
    nb = "nb"
    nn = "nn"
    en = "en"


class MultiLingualString(BaseModel):
    languageCode: LanguageCode
    value: str
    