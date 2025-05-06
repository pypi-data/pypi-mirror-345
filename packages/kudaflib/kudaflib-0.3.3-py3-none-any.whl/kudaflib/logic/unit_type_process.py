from rich.console import Console
from typing import Union, List, Dict, Tuple, Any, TypeVar 

from kudaflib.schemas.variable import (
    UnitTypeShort,
    UnitTypeMetadata,
    UnitTypeMetadataInput,
)   
from kudaflib.logic.utils import (
    validate_metadata_model
)
from kudaflib.config.settings import settings
from kudaflib.logic.connect import kudaf_metadata_connect


console = Console()

ModelType = TypeVar("ModelType")


class UnitTypeProcess:
    """
    This class contains logic for processing Unit Type Metadata
    """
    def query_existing_unittypes(
        self, 
        target_environment: str,
        catalog_id:int | None = None
    ) -> Dict[str, Any]:
        if catalog_id is not None:
            utypes_url = f"{settings.KUDAF_METADATA_BACKEND_URLS.get('unit_type_catalog')}{catalog_id}"
        else:
            utypes_url = f"{settings.KUDAF_METADATA_BACKEND_URLS.get('unit_type')}?global_only=false"

        retries = 5
        while retries > 0:
            errors, response_json = kudaf_metadata_connect.get(
                target_environment=target_environment,
                url_path=utypes_url,
                api_key_required=False,
            )
            if errors:
                console.print(f"[yellow]:disappointed: Error trying to fetch existing Kudaf-Metadata UnitTypes: {response_json.get('errors')} -> Retrying... :crossed_fingers:[/yellow]")
                retries -= 1
            else:
                break

        return response_json
    
    def create_unit_type(
        self,
        input_json: Dict[str, Any],
        target_environment: str,
        api_key: str,
    ):
        errors, response_json = kudaf_metadata_connect.post(
            target_environment=target_environment,
            resource="unit_type",
            input_json=input_json,
            api_key_required=True,
            api_key=api_key,
        )

        if errors:
            return {"errors": response_json.get("error", "An error occurred")}
        elif response_json.get("sync_results", {}).get('successful', {}).get('num', 0) != 1:
            return {"errors": response_json.get("sync_results", {}).get('errors', {}).get('detail', "")}
        else:
            msg, unittype_id = response_json.get("sync_results", {}).get('successful', {}).get('detail', "ID: ")[0].split("ID: ")
            return {"unittype_id": unittype_id, "msg": msg}
     
    def create_unittype_metadata(self, unittype_model_input: Dict | UnitTypeMetadataInput) -> Dict[str, Any]:
        """
        Creates the Unit Type metadata from the body input, for a given Catalog.
        """
        if isinstance(unittype_model_input, dict):
            utdict = unittype_model_input
        else:
            utdict = unittype_model_input.model_dump(exclude_unset=True, warnings='none')

        # Add a keyType field, as above
        utdict.update({
            "unitType": UnitTypeShort(**{
                "shortName": unittype_model_input.shortName,
                "name": unittype_model_input.name,
                "description": unittype_model_input.description,
            }),
        })

        utmodel = validate_metadata_model(Model=UnitTypeMetadata, metadata_json=utdict)             
        
        return utmodel.model_dump(exclude_unset=True)
    

unit_type_process = UnitTypeProcess()
