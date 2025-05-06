# Metadata models adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/model/metadata.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

from enum import Enum
from typing import Optional, Union, List, Dict, Any 

from pydantic import BaseModel, conlist, Extra


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


class UnitTypeGlobal(str, Enum):
    PERSON = "PERSON"
    ORGANISASJON = "ORGANISASJON"
    KOMMUNE = "KOMMUNE"
    FYLKE = "FYLKE"
    FYLKESKOMMUNE = "FYLKESKOMMUNE"


class MultiLingualString(BaseModel):
    languageCode: LanguageCode
    value: str


class DataRevision(BaseModel, extra=Extra.forbid):
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    temporalEndOfSeries: bool


class KeyType(BaseModel):
    name: str
    label: str
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]


class CodeListItem(BaseModel, extra=Extra.forbid):
    code: str
    categoryTitle: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    validFrom: Optional[Union[str, None]]
    validUntil: Optional[Union[str, None]]


class SentinelItem(BaseModel, extra=Extra.forbid):
    code: str
    categoryTitle: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]


class ValidPeriod(BaseModel, extra=Extra.forbid):
    start: Optional[Union[str, None]]
    start: Optional[Union[str, None]]


class ValueDomain(BaseModel, extra=Extra.forbid):
    description: Optional[Union[
        str, conlist(MultiLingualString, min_items=1)
    ]]
    measurementType: Optional[str]
    measurementUnitDescription: Optional[Union[
        str, conlist(MultiLingualString, min_items=1)
    ]    ]
    uriDefinition: Optional[List[Union[str, None]]]
    codeList: Optional[conlist(CodeListItem, min_items=1)]
    sentinelAndMissingValues: Optional[List[SentinelItem]]


class UnitTypeShort(BaseModel, extra=Extra.ignore):
    shortName: str
    name: conlist(MultiLingualString, min_items=1)
    description: conlist(MultiLingualString, min_items=1)


class UnitTypeMetadata(BaseModel, extra=Extra.ignore):
    shortName: str
    name: conlist(MultiLingualString, min_items=1)
    description: conlist(MultiLingualString, min_items=1)
    dataType: Optional[DataType]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]
    unitType: UnitTypeShort


class RepresentedVariable(BaseModel, extra=Extra.ignore):
    description: conlist(MultiLingualString, min_items=1)
    validPeriod: Optional[ValidPeriod]
    valueDomain: Optional[ValueDomain]


class InstanceVariable(BaseModel):
    name: str
    label: Optional[str]
    variableRole: Optional[str]
    dataType: Optional[DataType]
    format: Optional[str]
    keyType: Optional[KeyType]
    uriDefinition: Optional[List[Union[str, None]]]
    representedVariables: conlist(RepresentedVariable, min_items=1) 


class VariableMetadata(BaseModel, extra=Extra.ignore):
    name: str
    temporalityType: TemporalityType
    dataRetrievalUrl: Optional[str]  
    sensitivityLevel: SensitivityLevel
    populationDescription: Optional[conlist(Union[
        str, MultiLingualString
    ], min_items=1)]
    spatialCoverageDescription: Optional[conlist(Union[
        str, MultiLingualString
    ], min_items=1)]
    subjectFields: Optional[conlist(Union[
        str, conlist(MultiLingualString, min_items=1)
    ], min_items=1)]
    updatedAt: Optional[str]  
    dataRevision: Optional[DataRevision] 
    identifierVariables: conlist(InstanceVariable, min_items=1)
    measureVariables: conlist(InstanceVariable, min_items=1)
    attributeVariables: Optional[List[Dict[str, Any]]]


##################################################################
# INPUT YAML DATA: KUDAF METADATA DESCRIPTION (from CONFIG.YAML) #
##################################################################

class UnitTypeMetadataInput(BaseModel, extra=Extra.ignore):
    shortName: str
    name: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    dataType: Optional[DataType]
    format: Optional[str]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]


class IdentifierVariableInput(BaseModel, extra=Extra.forbid):
    unitType: Union[UnitTypeGlobal, UnitTypeMetadataInput]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable


class MeasureVariableInput(BaseModel, extra=Extra.ignore):
    unitType: Optional[Union[UnitTypeGlobal, UnitTypeMetadataInput]]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable
    label: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]  # 20231107 DD changed from 'name' to avoid confusion
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    dataType: Optional[DataType]
    uriDefinition: Optional[List[Union[str, None]]]
    format: Optional[str]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]


class VariableMetadataInput(VariableMetadata):
    identifierVariables: conlist(IdentifierVariableInput, min_items=1) 
    measureVariables: conlist(MeasureVariableInput, min_items=1) 


##########################
### DCAT INPUT SCHEMAS ###
##########################

class OrganizationMetadataInput(BaseModel):
    name: str                                               # foaf:name
    description: MultiLingualString | None = None           # dct:description
    identifier: str | None = None                           # dct:identifier

class PublisherMetadataInput(BaseModel):
    name: str                                               # foaf:name
    organization: OrganizationMetadataInput                 # dcatno:organization


class ContactMetadataInput(BaseModel):
    identifier: str | None = None                           # dct:identifier
    fullname: str  | None = None                            # foaf:name
    organization: OrganizationMetadataInput | None = None   # dcatno:organization
    phone: str | None = None                                # foaf:phone
    mbox: str | None = None                                 # foaf:mbox


class DatasetMetadataInput(BaseModel, extra=Extra.allow):
    catalogId: int
    dataset_id: str | None = None
    title: MultiLingualString                               # dct:title
    description: MultiLingualString | None = None           # dct:description
    contactPoint: List[ContactMetadataInput] | None = None  # dcat:contactPoint


class CatalogMetadataInput(BaseModel):
    title: MultiLingualString | None = None                 # dct:title
    description: MultiLingualString | None = None           # dct:description
    publisher: PublisherMetadataInput | None = None         # dct:publisher
    contactPoint: ContactMetadataInput | None = None        # dcat:contactPoint


############################################
#### DCAT OUTPUT TO DCAT-AP-NO SCHEMAS  ####
############################################

class AgentDCATOutput(BaseModel):
    identifier: str | None = None                           # dct:identifier
    name: Dict[str, str] | None = None                      # foaf:name
    organization_id: str | None = None                      # dcatno:organization
    organization_type: str | None = None                    # dcatno:organization


class ContactDCATOutput(AgentDCATOutput):
    fullname: str | None = None                             # foaf:name
    phone: str | None = None                                # foaf:phone
    mbox: str | None = None                                 # foaf:mbox


class PublisherDCATOutput(AgentDCATOutput):
    pass


class ThemeDCATOutput(BaseModel):
    identifier: str | None = None                           # dct:identifier
    title: Dict[str, str] | None = None                     # dct:title


class DatasetDCATOutput(BaseModel):
    identifier: str | None = None                           # dct:identifier
    title: Dict[str, str] | None = None                     # dct:title
    description: Dict[str, str] | None = None               # dct:description
    publisher: PublisherDCATOutput | None = None            # dct:publisher
    contactpoint: ContactDCATOutput | None = None           # dcat:contactPoint
    theme: List[str] | None = None                          # dcat:theme
    # theme: List[ThemeDCATOutput] | None = None              # dcat:theme


class DataserviceDCATOutput(DatasetDCATOutput):
    endpointURL: str | None = None                          # dcat:endpointURL
    endpointDescription: str | None = None                  # dcat:endpointDescription
    servesdatasets: List[DatasetDCATOutput] | None = None   # dcat:servesDataset
    media_types: List[str] | None = None                    # dcat:mediaType
