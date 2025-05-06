from typing import (
    Optional, 
    Union, 
    List, 
    Dict, 
    Any,
    Annotated
)
from pydantic import (
    BaseModel,
    ConfigDict, 
    AliasGenerator, 
)
from pydantic.alias_generators import to_camel
from annotated_types import Len

from kudaflib.schemas.helpers import (
    MultiLingualString, 
)
from kudaflib.schemas.variable import (
    UnitTypeMetadataInput,
    VariableMetadataInput,
)


###############################
### DCAT INPUT YAML SCHEMAS ###
###############################

class ThemeMetadataInput(BaseModel):
    identifier: Optional[str] = None                    # dct:identifier
    title: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]  

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
    )


class ContactMetadataInput(BaseModel):
    name: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                               # vcard:fn
    identifier: Optional[str]                       # dct:identifier
    mbox: Optional[str] = None                      # vcard:hasEmai
    url: Optional[str] = None                       # vcard:hasURL
    # name: str                                       # vcard:fn
    # has_email: Optional[str] = None                 # vcard:hasEmai
    # has_URL: Optional[str] = None                   # vcard:hasURL

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
    )


class OrganizationMetadataInput(BaseModel):
    name: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                       # foaf:name
    description: Optional[Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]] = None                                                     # dct:description
    identifier: str                                         # dct:identifier
    type: Optional[str]                                     # dct:type
    contact_point: Optional[ContactMetadataInput] = None    # dcat:contactPoint

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
    )


class DatasetMetadataInput(BaseModel, extra='ignore'):
    identifier: Optional[str] = None
    # catalog: CatalogMetadataInput  # -> Use just to make the connection
    title: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                      # dct:title
    description: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                      # dct:description
    theme: Union[
        List[str], Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                       # dct:theme
    # contact_point: Optional[ContactMetadataInput] = None  # dcat:contactPoint -> TODO: STANDARD SAYS IT'S A  LIST ! Copy from Catalog.contact_point
    contact_point: Optional[ContactMetadataInput] = None  # dcat:contactPoint -> Copy from Catalog.contact_point
    publisher: Optional[OrganizationMetadataInput] = None          # dct:publisher
    landing_page: Optional[str] = None                             # dcat:landingPage
    spatial: Optional[List[str]] = None                                  # dct:spatial
    keyword: Optional[Dict[str, str]] = None                           # dcat:keyword
    variables: Optional[List[VariableMetadataInput]] = None

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
    )


class CatalogMetadataInput(BaseModel, extra='ignore'):
    identifier: Optional[str] = None
    title: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                     # dct:title
    description: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                     # dct:description
    publisher: OrganizationMetadataInput                  # dct:publisher
    contact_point: Optional[ContactMetadataInput] = None  # dcat:contactPoint  -> Copy from Organization.contact_point  
    theme: Optional[Union[
        List[str], Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]] = None                                              # dct:theme
    unittypes: Optional[List[UnitTypeMetadataInput]] = None
    datasets: Optional[List[DatasetMetadataInput]] = None  # dct:dataset                 

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
    )


###################################################
#### DCAT INPUT TO KUDAF-METADATA API SCHEMAS  ####
###################################################

class ContactAPIInput(BaseModel, extra='allow'):
    identifier: str | None = None                           # dct:identifier
    fullname: str  | None = None                            # foaf:name
    organization: OrganizationMetadataInput | None = None   # dcatno:organization
    phone: str | None = None                                # foaf:phone
    mbox: str | None = None                                 # foaf:mbox


class OrganizationAPIInput(BaseModel, extra='allow'):
    identifier: str | None = None                           # dct:identifier
    name: str                                               # foaf:name
    description: MultiLingualString | None = None           # dct:description


class PublisherAPIInput(BaseModel, extra='allow'):
    name: str                                # foaf:name
    organization: OrganizationAPIInput                 # dcatno:organization


class CatalogAPIInput(BaseModel, extra='allow'):
    title: MultiLingualString                 # dct:title
    description: MultiLingualString           # dct:descriptioncat
    publisher: PublisherAPIInput         # dct:publisher
    contactPoint: ContactAPIInput | None = None        # dcat:contactPoint


class DatasetAPIInput(BaseModel, extra='allow'):
    catalogId: int | None = None   # Actually compulsory, but needs to be added after Catalog creation
    dataset_id: str | None = None
    title: MultiLingualString                               # dct:title
    description: MultiLingualString | None = None           # dct:description
    contactPoint: ContactAPIInput | None = None  # dcat:contactPoint
    # contactPoint: List[ContactAPIInput] | None = None  # dcat:contactPoint


############################################
#### DCAT OUTPUT TO DCAT-AP-NO SCHEMAS  ####
############################################

class ContactDCATOutput(BaseModel):
    name: str                                           # vcard:fn
    has_email: Optional[str] = None                     # vcard:hasEmai
    has_URL: Optional[str] = None                       # vcard:hasURL
    
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        from_attributes=True,
    )


class OrganizationDCATOutput(BaseModel):
    name: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                   # foaf:name
    identifier: Optional[str]                           # dct:identifier
    type: Optional[str]                                 # dct:type
    contact_point: Optional[ContactDCATOutput] = None   # dcat:contactPoint

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        from_attributes=True,
    )


class DatasetDCATOutput(BaseModel):
    identifier: Optional[str] = None                           # dct:identifier
    title: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                           # dct:title
    description: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                         # dct:description
    theme: Annotated[List[str], Len(min_length=1)]      # dcat:theme
    contact_point: Optional[List[ContactMetadataInput]] = None  # dcat:contactPoint -> Copy from Catalog.contact_point
    publisher: Optional[OrganizationDCATOutput] = None          # dct:publisher
    landing_page: Optional[str] = None                           # dcat:landingPage
    spatial: Optional[str] = None                               # dct:spatial
    keyword: Optional[List[str]] = None                        # dcat:keyword

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        from_attributes=True,
    )


class DataserviceDCATOutput(DatasetDCATOutput):
    endpoint_URL: Optional[str]                          # dcat:endpointURL
    endpoint_description: Optional[str]                 # dcat:endpointDescription
    servesdatasets: Optional[List[DatasetDCATOutput]]   # dcat:servesDataset
    media_types: Optional[List[str]]                    # dcat:mediaType
    
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        from_attributes=True,
    )


class CatalogDCATOutput(DatasetDCATOutput):
    title: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                           # dct:title
    description: Union[
        str, Annotated[List[Dict[str, Any]], Len(min_length=1)]
    ]                                                           # dct:description    
    contact_point: ContactDCATOutput                            # dcat:contactPoint
    identifier: Optional[str] = None                            # dct:identifier
    theme: Optional[List[str]] = None                           # dcat:theme
    landing_page: Optional[str] = None                           # dcat:landingPage
    dataset: Optional[List[DatasetDCATOutput]] = None           # dcat:dataset
    data_service: Optional[List[DataserviceDCATOutput]] = None  # dcat:dataservice

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
        from_attributes=True,
    )
