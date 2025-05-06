# Metadata models adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/model/metadata.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

from enum import Enum
from typing import (
    Optional, 
    Union, 
    List, 
    Dict, 
    Any,
    Annotated
)
from pydantic import BaseModel
from annotated_types import Len

from kudaflib.schemas.helpers import (
    MultiLingualString,
    DataType,
    TemporalityType,
    SensitivityLevel,
)


class UnitTypeGlobal(str, Enum):
    PERSON = "PERSON"
    ORGANISASJON = "ORGANISASJON"
    KOMMUNE = "KOMMUNE"
    FYLKE = "FYLKE"
    FYLKESKOMMUNE = "FYLKESKOMMUNE"


class DataRevision(BaseModel, extra='forbid'):
    description: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]

    ]
    temporalEndOfSeries: bool


class KeyType(BaseModel):
    name: str
    label: str
    description: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]


class CodeListItem(BaseModel, extra='forbid'):
    code: str
    categoryTitle: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]
    validFrom: Optional[Union[str, None]] = None
    validUntil: Optional[Union[str, None]] = None


class SentinelItem(BaseModel, extra='forbid'):
    code: str
    categoryTitle: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]


class ValidPeriod(BaseModel, extra='forbid'):
    start: Optional[Union[str, None]] = None
    start: Optional[Union[str, None]] = None


class ValueDomain(BaseModel, extra='forbid'):
    description: Optional[Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]] = None
    measurementType: Optional[str] = None
    measurementUnitDescription: Optional[Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]] = None
    uriDefinition: Optional[List[Union[str, None]]] = None
    codeList: Optional[Annotated[List[CodeListItem], Len(min_length=1)]] = None
    sentinelAndMissingValues: Optional[List[SentinelItem]] = None

class RepresentedVariable(BaseModel, extra='ignore'):
    description: Annotated[List[MultiLingualString], Len(min_length=1)]
    validPeriod: Optional[ValidPeriod] = None
    valueDomain: Optional[ValueDomain] = None


class InstanceVariable(BaseModel):
    name: str
    label: Optional[str] = None
    variableRole: Optional[str] = None
    dataType: Optional[DataType] = None
    format: Optional[str] = None
    keyType: Optional[KeyType] = None
    uriDefinition: Optional[List[Union[str, None]]] = None
    representedVariables: Annotated[List[RepresentedVariable], Len(min_length=1)] 


class VariableMetadata(BaseModel, extra='ignore'):
    name: str
    temporalityType: TemporalityType
    dataRetrievalUrl: Optional[str] = None  
    sensitivityLevel: SensitivityLevel
    populationDescription: Optional[Union[
        Annotated[List[str], Len(min_length=1)],
        Annotated[List[MultiLingualString], Len(min_length=1)]
    ]] = None
    spatialCoverageDescription: Optional[Union[
        Annotated[List[str], Len(min_length=1)],
        Annotated[List[MultiLingualString], Len(min_length=1)]
    ]] = None
    subjectFields: Optional[Union[
        Annotated[List[str], Len(min_length=1)],
        Annotated[List[MultiLingualString], Len(min_length=1)],
        Annotated[List[List[Dict[str, Any]]], Len(min_length=1)]
    ]] = None
    updatedAt: Optional[str] = None  
    dataRevision: Optional[DataRevision] = None 
    identifierVariables: Annotated[List[InstanceVariable], Len(min_length=1)]
    measureVariables: Annotated[List[InstanceVariable], Len(min_length=1)]
    attributeVariables: Optional[List[Dict[str, Any]]] = None


class UnitTypeShort(BaseModel, extra='ignore'):
    shortName: str
    name: Annotated[List[MultiLingualString], Len(min_length=1)]
    description: Annotated[List[MultiLingualString], Len(min_length=1)]


class UnitTypeMetadata(BaseModel, extra='ignore'):
    shortName: str
    name: Annotated[List[MultiLingualString], Len(min_length=1)]
    description: Annotated[List[MultiLingualString], Len(min_length=1)]
    dataType: Optional[DataType] = None
    valueDomain: Optional[ValueDomain] = None
    validPeriod: Optional[ValidPeriod] = None
    unitType: UnitTypeShort

##################################################################
# INPUT YAML DATA: KUDAF METADATA DESCRIPTION (from CONFIG.YAML) #
##################################################################

class UnitTypeMetadataInput(BaseModel, extra='ignore'):
    shortName: str
    name: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]
    description: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]
    dataType: Optional[DataType] = None
    format: Optional[str] = None
    valueDomain: Optional[ValueDomain] = None
    validPeriod: Optional[ValidPeriod] = None


class IdentifierVariableInput(BaseModel, extra='forbid'):
    unitType: Union[UnitTypeGlobal, UnitTypeMetadataInput, str]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable


class MeasureVariableInput(BaseModel, extra='ignore'):
    unitType: Optional[Union[UnitTypeGlobal, UnitTypeMetadataInput, str]] = None  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable
    label: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]  # 20231107 DD changed from 'name' to avoid confusion
    description: Union[
        str, Annotated[List[MultiLingualString], Len(min_length=1)]
    ]
    dataType: Optional[DataType] = None
    uriDefinition: Optional[List[str]] = None
    format: Optional[str] = None
    valueDomain: Optional[ValueDomain] = None
    validPeriod: Optional[ValidPeriod] = None


class VariableMetadataInput(VariableMetadata):
    # dataset: Optional[DatasetMetadataInput] = None  # -> Use just to make the connection when creating the metadata
    identifierVariables: Annotated[List[IdentifierVariableInput], Len(min_length=1)] 
    measureVariables: Annotated[List[MeasureVariableInput], Len(min_length=1)] 


########################################################
#### VARIABLES INPUT TO KUDAF-METADATA API SCHEMAS  ####
########################################################


class UnitTypeAPIInput(BaseModel, extra='forbid'):
    catalog_id: int
    unit_type: UnitTypeMetadataInput


class VarToUnitTypeLinkAPIInput(BaseModel):
    unit_type_id: int
    # key_role: INSTANCE_VARIABLE_ROLE


class MeasureVariableAPIInput(MeasureVariableInput, extra='ignore'):
    # unitType: Optional[Union[kudaflib_UnitTypeGlobal, VarToUnitTypeLinkAPIInput]]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable
    unitType: Optional[VarToUnitTypeLinkAPIInput] = None
    

class VariableMetadataAPIInput(VariableMetadataInput, extra='forbid'):
    identifierVariables: Annotated[List[VarToUnitTypeLinkAPIInput], Len(min_length=1)] 
    measureVariables: Annotated[List[MeasureVariableAPIInput], Len(min_length=1)] 


class VariablesAPIInput(BaseModel, extra='forbid'):
    dataset_id: str
    variables: Annotated[List[VariableMetadataAPIInput], Len(min_length=1)]
