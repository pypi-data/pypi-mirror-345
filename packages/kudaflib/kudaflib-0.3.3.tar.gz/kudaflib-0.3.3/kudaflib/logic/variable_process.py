import pydantic
from typing import Union, List, Dict, Tuple, Any, TypeVar 

from kudaflib.schemas.helpers import (
    MultiLingualString,
)
from kudaflib.schemas.variable import (
    VariableMetadataInput,
    VariableMetadata,
    UnitTypeMetadataInput,
    UnitTypeMetadata,
    InstanceVariable,
    RepresentedVariable,
    KeyType,
    ValueDomain,
    UnitTypeGlobal,
)
from kudaflib.logic.unit_type_process import unit_type_process
from kudaflib.logic.connect import kudaf_metadata_connect
from kudaflib.logic.utils import (
    format_pydantic_error,
    validate_metadata_model,
    replace_enums,
    convert_to_multilingual_dict,
    convert_list_to_multilingual,
    unittype_to_multilingual,
    value_domain_to_multilingual,
)
from kudaflib.logic.exceptions import (
    ValidationError,
    UnregisteredUnitTypeError,
    ParseMetadataError,
)
from kudaflib.metadata import (
    temporal_attributes,
    unit_type_variables,
)


ModelType = TypeVar("ModelType")


class VariableProcess:
    """
    This class contains logic for processing Variable Metadata
    """
    def create_variable(
        self,
        input_json: Dict[str, Any],
        target_environment: str,
        api_key: str,
    ) -> Dict[str, Any]:
        # Create Variable Metadata via the API
        errors, response_json = kudaf_metadata_connect.post(
            target_environment=target_environment,
            resource="variable",
            input_json=input_json,
            api_key_required=True,
            api_key=api_key,
        )

        if errors:
            return {"errors": response_json.get("error", "An error occurred")}
        elif response_json.get("sync_results", {}).get('successful', {}).get('num', 0) != 1:
            return {"errors": response_json.get("sync_results", {}).get('errors', {}).get('detail', "")}
        else:
            variable_id = response_json.get("sync_results", {}).get('successful', {}).get('detail', [{"inserted_var_id": "missing"}])[0].get('inserted_var_id', ["missing"])[0]
            error_msg = response_json.get("sync_results", {}).get('errors', {}).get('detail', [{}])[0].get('msgs')

            return {"variable_id": variable_id, "errors": error_msg}
        
    def insert_instance_variables(self, metadata_input: VariableMetadataInput) -> Tuple[List, Dict]:
        """
        Create instance variable metadata for Identifier, Measure and Attibute Variables
        Create metadata for Datasource-specific Unit Types, if any
        """
        # Identifier Variables: 
        # Could come from pre-defined Global Unit Types or from provided Datasource-specific Unit Types
        ivars = []
        ds_units = []
        for _iv in metadata_input.identifierVariables:
            _utype = _iv.unitType
            if not isinstance(_utype, UnitTypeMetadataInput):
                # This may be a Global Unit Type
                if hasattr(_utype, 'value'):
                    _uname = _utype.value
                else:
                    _uname = _utype

                if _uname in UnitTypeGlobal._member_names_ and _uname in unit_type_variables.GLOBAL_UNIT_TYPES:
                    _ivmodel = self.convert_unit_type_to_identifier(unit_type_variables.get(_uname))
                    ivars.append(replace_enums(input_dict=_ivmodel.model_dump(exclude_unset=True)))
        
            elif isinstance(_utype, UnitTypeMetadataInput):
                # This is a datasource-specific UnitType
                # First create an Identifier Variable out of it (an InstanceVariable)
                if isinstance(_iv.unitType.name, str):
                    # Extract if string before converting to dicts
                    _label = _iv.unitType.name
                elif isinstance(_iv.unitType.name, list):
                    # Pick first item in the list, typically the default language
                    _name = _iv.unitType.name[0]
                    if isinstance(_name, dict):
                        _label = _name.get('value', "")
                    elif isinstance(_name, str):
                        _label = _name
                    elif isinstance(_name, MultiLingualString):
                        _label = _name.value
                    else:
                        _label = "N/A"
                else:
                    _label = "N/A"

                _utype = unittype_to_multilingual(utype=_utype, default_lang="no")
                _ivdict = {
                    "name": _utype.shortName,
                    "label": _label,
                    "dataType": _iv.unitType.dataType,
                    "variableRole": "Identifier",
                    "keyType": KeyType(**{
                        "name": _utype.shortName,
                        "label": _label,
                        "description": _utype.description,
                    }),
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": _utype.description,
                            "valueDomain": _utype.valueDomain,
                        })
                    ]
                }
                _ivmodel = validate_metadata_model(Model=InstanceVariable, metadata_json=_ivdict)
                ivars.append(replace_enums(_ivdict))   

                # Now create the metadata for this new UnitType
                _utype_metadata = unit_type_process.create_unittype_metadata(unittype_model_input=_utype)
                ds_units.append(_utype_metadata)
            else:
                error = f"Unregistered Unit Type: {_utype}"
                print(error)
                raise UnregisteredUnitTypeError(error)
            
        # Measure Variables 
        mvars = []
        for _mv in metadata_input.measureVariables:
            insert_measure = {}
            _mvdict = _mv.model_dump(exclude_unset=True)
            _utype = _mvdict.get("unitType", "")

            insert_measure["name"] = metadata_input.name
            insert_measure["label"] = _mvdict["label"]
            insert_measure["description"] = _mvdict["description"] if isinstance(_mvdict["description"], list) else [
                            convert_to_multilingual_dict(input_str=_mvdict["description"], default_lang="no")
                        ]
            insert_measure["variableRole"] = "Measure"

            if _utype:
                if not isinstance(_utype, UnitTypeMetadataInput) and \
                    hasattr(_utype, 'value') and \
                    _utype.value in unit_type_variables.UnitTypeGlobal._member_names_ and \
                    _utype in unit_type_variables.GLOBAL_UNIT_TYPES:
                    utmodel = UnitTypeMetadataInput(**unit_type_variables.get(_utype))
                elif isinstance(_utype, str) and _utype in unit_type_variables.GLOBAL_UNIT_TYPES:
                    utmodel = UnitTypeMetadataInput(**unit_type_variables.get(_utype))
                elif isinstance(_utype, dict):
                    utmodel = UnitTypeMetadataInput(**_utype)
                    utmodel = unittype_to_multilingual(utype=utmodel, default_lang="no")
                    # Now create the metadata for this new UnitType
                    _mutype_metadata = unit_type_process.create_unittype_metadata(unittype_model_input=utmodel)
                    ds_units.append(_mutype_metadata)
                elif type(_utype) not in [str, UnitTypeMetadataInput]:
                    print(f"UNIT TYPE: {_utype} NOT FOUND for Measure: {metadata_input.name}")
                    raise UnregisteredUnitTypeError
                else:
                    print(f"UNIT TYPE: {_utype} NOT FOUND for Measure: {metadata_input.name}")
                    raise UnregisteredUnitTypeError

                insert_measure.update({
                    "keyType": KeyType(**{
                        "name": utmodel.shortName,
                        "label":utmodel.name[0].get('value', "") if isinstance(utmodel.name[0], dict) else utmodel.name[0].value,
                        "description": utmodel.description if isinstance(utmodel.description, list) else [
                            convert_to_multilingual_dict(input_str=utmodel.description, default_lang="no")
                        ],
                    }),
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": _mvdict["description"] if isinstance(_mvdict["description"], list) else [
                            convert_to_multilingual_dict(input_str=_mvdict["description"], default_lang="no")
                        ],
                            "valueDomain": utmodel.valueDomain,
                        })
                    ]
                })
            else:
                insert_measure.update({
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": _mvdict["description"] if isinstance(_mvdict["description"], list) else [
                                convert_to_multilingual_dict(input_str=_mvdict["description"], default_lang="no")
                            ],
                            "valueDomain": value_domain_to_multilingual(
                                val_dom=_mvdict.get('valueDomain') if _mvdict.get('valueDomain') else ValueDomain(**{
                                        "uriDefinition": None,
                                        "description": "N/A",
                                        "measurementUnitDescription": "N/A"
                                }), 
                                default_lang="no"
                            ),
                        })
                    ]
                })

            _mvmodel = validate_metadata_model(Model=InstanceVariable, metadata_json=insert_measure)         
            mvars.append(replace_enums(input_dict=insert_measure)) #_mvmodel.model_dump(exclude_unset=True)))

        # Attribute Variables
        attrvars = [
            temporal_attributes.generate_start_time_attribute(metadata_input.temporalityType),
            temporal_attributes.generate_stop_time_attribute(metadata_input.temporalityType),
        ] # + metadata_input.get("attributeVariables", [])

        instance_vars = {
            "identifierVariables": ivars,
            "measureVariables": mvars,
            "attributeVariables": attrvars,
        }

        return ds_units, instance_vars

    def convert_unit_type_to_identifier(self, utype: Dict) -> InstanceVariable:
        try:
            utmodel = UnitTypeMetadata(**utype)
            ivmodel = InstanceVariable(**{
                "name": utmodel.shortName,
                "label": utmodel.name[0].value,
                "dataType": utmodel.dataType,
                "variableRole": "Identifier",
                "keyType": KeyType(**{
                    "name": utmodel.unitType.shortName,
                    "label": utmodel.unitType.name[0].value,
                    "description": utmodel.unitType.description,
                }),
                "representedVariables": [
                    RepresentedVariable(**{
                        "description": utmodel.description,
                        "valueDomain": utmodel.valueDomain,
                    })
                ]
            })
        except pydantic.ValidationError as e:
            error_messages = [
                format_pydantic_error(error) for error in e.errors()
            ]
            print(f"Metadata file validation errors: {error_messages}")
            raise ValidationError("metadata file", errors=error_messages)
        except Exception as e:
            print(e)
            raise e 
        return ivmodel

    def convert_descriptions_to_multilingual(
        self, 
        metadata_input: VariableMetadataInput, 
        default_lang: str = "no"
    ) -> Dict[str, Any]:
        multi_dict = {}
        multilingual_fields = ["populationDescription", "spatialCoverageDescription", "subjectFields"]
        nested_list_fields = ["subjectFields"]
        # Convert string fields to Norwegian multilungual strings if needed
        for field in multilingual_fields:
            field_contents = getattr(metadata_input, field)
            if isinstance(field_contents, list):
                if field in nested_list_fields:
                    multi_dict[field] = convert_list_to_multilingual(
                        input_list=field_contents, 
                        default_lang=default_lang,
                        nested_list=True)
                else:
                    multi_dict[field] = convert_list_to_multilingual(input_list=field_contents, default_lang=default_lang)

        return multi_dict


variable_process = VariableProcess()
