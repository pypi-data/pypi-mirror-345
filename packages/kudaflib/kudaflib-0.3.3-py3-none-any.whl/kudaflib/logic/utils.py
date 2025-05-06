import json
import os
import uuid 
import pydantic
from ruamel.yaml import YAML
from pathlib import Path
from typing import Tuple, Union, List, Dict, TypeVar, Any
from enum import Enum

from kudaflib.schemas.variable import (
    MultiLingualString,
    ValueDomain,
    UnitTypeMetadataInput,
)
from kudaflib.logic.exceptions import ParseMetadataError, ValidationError


ModelType = TypeVar("ModelType")


def get_multilingual_value_string(input_dict: Dict) -> str:
    """
    Extracts the value from a multi-lingual dictionary
    """
    value_list = []
    lang_list = ["no", "nb" "nn", "en"]

    for lang in lang_list:
        value = input_dict.get(lang, "")
        if value:
            value_list.append(value)

    return value_list[0] if value_list else ""


def format_pydantic_error(error: Dict) -> str:
    location = "->".join(
        loc for loc in error["loc"] if loc != "__root__" and not isinstance(loc, int)
    )
    return f'{location}: {error["msg"]}' 


def validate_metadata_model(Model: ModelType, metadata_json: Dict) -> ModelType:
    try:
        model_obj = Model(**metadata_json)  
    except pydantic.ValidationError as e:
        error_messages = [
            format_pydantic_error(error) for error in e.errors()
        ]
        print(f"Metadata file validation errors: {error_messages}")
        raise ValidationError("metadata file", errors=error_messages)
    except Exception as e:
        print(e)
        raise e
    
    return model_obj


def remove_directory_files(
    directory: Path,
) -> bool:
    if not directory.is_dir():
        return False
    
    for filename in directory.iterdir():
        if not filename.is_file():
            continue 
        else:
            os.remove(filename)

    return True


def check_filepaths_validity(paths: List[Union[Path, str]]) -> bool:
    for p in paths:
        if p and not Path.exists(p):
            raise ParseMetadataError(f'File not found: {p}')
        
    return True


def safe_file_open_w(path:str):
    ''' 
    Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)

    return open(path, 'w', newline='')


def check_or_create_directory(
    directory: Union[str, None]
) -> Tuple[Path, bool]:
    """
    Generates a directory if the supplied one does not exist.
    Returns a tuple with:
        * The directory's Path
        * True, if directory was generated. False if not.
    """
    if directory:
        return Path(directory), False
    else:
        os.mkdir(directory)
        return Path(directory), True
    

def load_yaml(filepath: Path) -> dict:
    yaml = YAML()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.load(f)
    except Exception as e:
        print(f"Failed to open file at {str(filepath)} - ERROR: {str(e)}")
        raise e


def replace_enums(input_dict: Dict) -> Dict:
    """
    Recursively replaces all instances of Enum inside a Dict
    with their value
    """
    output = {}
    for k, v in input_dict.items():
        if isinstance(v, dict):
            output[k] = replace_enums(input_dict=v)

        elif isinstance(v, Enum):
            output[k] = v.value

        elif isinstance(v, list):
            output_list = []
            for item in v:
                if isinstance(item, dict):
                    # Go recursive
                    output_list.append(replace_enums(input_dict=item))

                elif isinstance(item, Enum):
                    output_list.append(item.value)

                else:
                    output_list.append(item)
            output[k] = output_list

        else:
            output[k] = v
        
    return output


def convert_to_multilingual_dict(input_str: str, default_lang: str = "no") -> Dict:
    return {
        "languageCode": default_lang,
        "value": input_str,
    }


def convert_list_to_multilingual(input_list: List, default_lang: str = "no", nested_list: bool = False) -> list[Dict]:
    """
    Convert lists into multi-lingual Dict lists, recursively if needed 
    """
    new_list = []
    for item in input_list:
        if isinstance(item, str):
            if nested_list:
                # Insert within a list
                new_list.append([ convert_to_multilingual_dict(input_str=item, default_lang=default_lang) ])
            else:
                new_list.append(convert_to_multilingual_dict(input_str=item, default_lang=default_lang))

        elif isinstance(item, MultiLingualString):
            new_list.append(replace_enums(input_dict=item.model_dump()))

        elif isinstance(item, list):
            # Go recursive
            new_list.append(convert_list_to_multilingual(input_list=item, default_lang=default_lang))

        else:
            print(f"Type not allowed - Multi-lingual string: {item}")
            raise ParseMetadataError

    return new_list


def value_domain_to_multilingual(val_dom: ValueDomain, default_lang: str = "no") -> ValueDomain:
    """
    Convert ValueDomain string fields to Norwegian multilungual strings if needed
    """
    for field in ["description", "measurementUnitDescription"]:
        if isinstance(getattr(val_dom, field), str):
            setattr(val_dom, field, [ 
                convert_to_multilingual_dict(input_str=getattr(val_dom, field), default_lang=default_lang) 
            ])
    
    if val_dom.codeList:
        for code_item in val_dom.codeList:
            if isinstance(code_item.categoryTitle, str):
                code_item.categoryTitle = [ 
                    convert_to_multilingual_dict(input_str=code_item.categoryTitle, default_lang=default_lang) 
                ]

    if val_dom.sentinelAndMissingValues:
        for code_item in val_dom.sentinelAndMissingValues:
            if isinstance(code_item.categoryTitle, str):
                code_item.categoryTitle = [ 
                    convert_to_multilingual_dict(input_str=code_item.categoryTitle, default_lang=default_lang) 
                ]

    return val_dom


def unittype_to_multilingual(utype: UnitTypeMetadataInput, default_lang: str = "no") -> UnitTypeMetadataInput:
    """ 
    Convert UnitType string fields to Norwegian multilungual strings if needed
    """
    for field in ["name", "description"]:
        if isinstance(getattr(utype, field), str):
            setattr(utype, field, [ 
                convert_to_multilingual_dict(input_str=getattr(utype, field), default_lang=default_lang) 
            ])
    
    utype.valueDomain = value_domain_to_multilingual(
        val_dom=utype.valueDomain if utype.valueDomain else ValueDomain(**{
                "uriDefinition": None,
                "description": "N/A",
                "measurementUnitDescription": "N/A"
        }), 
        default_lang=default_lang
    )

    return utype 


def convert_to_multilingual_literal(
    input_str_dict: str | MultiLingualString | Dict[str, str],
    default_lang: str = "no"
) -> Dict[str, Any]:
    if isinstance(input_str_dict, str):
        return {
                default_lang: input_str_dict,
        }  
    elif isinstance(input_str_dict, MultiLingualString):
        input_dict = replace_enums(input_dict=input_str_dict.model_dump())
        return {
            input_dict.get('languageCode', default_lang): input_dict.get('value', 'N/A')
        }   
    elif isinstance(input_str_dict, dict):
        # Just pass-through, without Enums
        input_dict = replace_enums(input_dict=input_str_dict)
        return input_dict   
    else:
        return {
            "error": "Incorrect input type, must be either string or MultiLingualString or Dict"
        }


def convert_list_to_multilingual_literals(
    input_list: List, 
    default_lang: str = "no", 
    nested_list: bool = False
) -> List:
    """
    Convert lists into multi-lingual Dict lists, recursively if needed 
    """
    new_list = []
    for item in input_list:
        if isinstance(item, str):
            if nested_list:
                # Insert within a list
                new_list.append([convert_to_multilingual_literal(
                    input_str_dict=item, 
                    default_lang=default_lang
                )])
            else:
                new_list.append(convert_to_multilingual_literal(
                    input_str_dict=item, 
                    default_lang=default_lang
                ))

        elif isinstance(item, MultiLingualString):
            input_dict = replace_enums(input_dict=item.model_dump())
            new_list.append({
                input_dict.get('languageCode', default_lang): input_dict.get('value', 'N/A')
            })

        elif isinstance(item, list):
            # Go recursive
            new_list.append(convert_list_to_multilingual_literals(input_list=item, default_lang=default_lang))

        else:
            print(f"Type not allowed - Multi-lingual string: {item}")
            raise ParseMetadataError

    return new_list


# Below functions from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/adapter/local_storage.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

def load_json(filepath: Path) -> Dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to open file at {str(filepath)}")
        raise e


def write_json(filepath: Path, content: Dict) -> None:
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(content, json_file, indent=4, ensure_ascii=False)


def resolve_working_directory(
    working_directory: Union[str, None]
) -> Tuple[Path, bool]:
    """
    Generates a working directory if a working directory is not supplied.
    Returns a tuple with:
        * The working directory Path
        * True, if directory was generated. False if not.
    """
    if working_directory:
        return Path(working_directory), False
    else:
        generated_working_directory = Path(str(uuid.uuid4()))
        os.mkdir(generated_working_directory)
        return generated_working_directory, True
