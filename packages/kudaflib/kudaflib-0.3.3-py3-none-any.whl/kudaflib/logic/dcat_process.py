from rich.console import Console
from typing import Union, List, Dict, Tuple, Any, TypeVar 
from pydantic import BaseModel
from datacatalogtordf import (
    Catalog, 
    Dataset, 
    Distribution,
    Agent, 
    Contact,
    URI,
    InvalidURIError, 
)

from kudaflib.config.settings import settings
from kudaflib.schemas.variable import (
    UnitTypeShort,
    UnitTypeMetadata,
    UnitTypeMetadataInput,
)   
from kudaflib.logic.utils import (
    validate_metadata_model,
    convert_to_multilingual_dict,
    convert_to_multilingual_literal,
    convert_list_to_multilingual,
    convert_list_to_multilingual_literals,
)
from kudaflib.logic.connect import kudaf_metadata_connect


console = Console()


class DCATProcess:
    """
    This class contains logic for processing DCAT Metadata (Catalog, Dataset)
    """
    def query_existing_catalogs(
        self,
        target_environment: str,
        catalog_id: int = None,
        include_datasets: bool = False,
        include_variables: bool = False,
    ) -> Dict[str, Any]:
        cats_url = f"{settings.KUDAF_METADATA_BACKEND_URLS.get('catalog')}"

        if catalog_id:
            cats_url += f"{catalog_id}"

        if include_datasets:
            cats_url += "?include_datasets=true"
        elif include_variables:
            cats_url += "?include_variables=true"

        retries = 5
        while retries > 0:
            errors, response_json = kudaf_metadata_connect.get(
                target_environment=target_environment,
                url_path=cats_url,
                api_key_required=False,
            )
            if errors:
                console.print(f"[yellow]:disappointed: Error trying to fetch existing Kudaf-Metadata Catalogs: {response_json.get('errors')} -> Retrying... :crossed_fingers:[/yellow]")
                retries -= 1
            else:
                break

        return response_json

    def query_existing_datasets(
        self,
        target_environment: str,
        dataset_id: int = None,
        include_variables: bool = False,
    ) -> List[Dict[str, Any]]:
        ds_url = f"{settings.KUDAF_METADATA_BACKEND_URLS.get('dataset')}"

        if dataset_id:
            ds_url += f"{dataset_id}"
            
        if include_variables:
            ds_url += "?include_variables=true"

        retries = 5
        while retries > 0:
            errors, response_json = kudaf_metadata_connect.get(
                target_environment=target_environment,
                url_path=ds_url,
                api_key_required=False,
            )
            if errors:
                console.print(f"[yellow]:disappointed: Error trying to fetch existing Kudaf-Metadata Datasets: {response_json.get('errors')} -> Retrying... :crossed_fingers:[/yellow]")
                retries -= 1
            else:
                break

        return response_json
    
    def create_catalog(
        self,
        input_json: Dict[str, Any],
        target_environment: str,
        api_key: str,
    ):
        errors, response_json = kudaf_metadata_connect.post(
            target_environment=target_environment,
            resource="catalog",
            input_json=input_json,
            api_key_required=True,
            api_key=api_key,
        )

        if errors:
            return {"errors": response_json.get("error", "An error occurred")}
        elif response_json.get("sync_results", {}).get('successful', {}).get('num', 0) != 1:
            return {"errors": response_json.get("sync_results", {}).get('errors', {}).get('detail', "")}
        else:
            catalog_id = response_json.get("catalog", {}).get('id', 0)
            catalog_name = response_json.get("catalog", {}).get('name', "")
            return {"catalog_id": catalog_id, "catalog_name": catalog_name}
        
    def create_dataset(
        self,
        input_json: Dict[str, Any],
        target_environment: str,
        api_key: str,
    ):
        errors, response_json = kudaf_metadata_connect.post(
            target_environment=target_environment,
            resource="dataset",
            input_json=input_json,
            api_key_required=True,
            api_key=api_key,
        )
 
        if errors:
            return {"errors": response_json.get("error", "An error occurred")}
        elif response_json.get("sync_results", {}).get('successful', {}).get('num', 0) != 1:
            return {"errors": response_json.get("sync_results", {}).get('errors', {}).get('detail', "")}
        else:
            dataset_id = response_json.get("dataset", {}).get('id', 0)
            dataset_title = response_json.get("dataset", {}).get('title', "")
            return {"dataset_id": dataset_id, "dataset_name": dataset_title}
    
    @staticmethod
    def convert_fields_to_multilingual(
        metadata_input_model: Any, 
        default_lang: str = "no"
    ) -> Dict[str, Any]:
        """
        Converts string fields in a DCAT Metadata Input Model to Norwegian multilingual strings
        of the form {"no": "string"}
        """
        multi_dict = {}
        multilingual_fields = ["title", "name", "description", "keywords", "subjectFields"]
        nested_list_fields = ["subjectFields"]

        # Convert string fields to Norwegian multilungual strings if needed
        for field in multilingual_fields:
            field_contents = getattr(metadata_input_model, field, None)
            if field_contents is None:
                continue
            if isinstance(field_contents, list):
                if field in nested_list_fields:
                    multi_dict[field] = convert_list_to_multilingual(
                        input_list=field_contents, 
                        default_lang=default_lang,
                        nested_list=True)
                else:
                    multi_dict[field] = convert_list_to_multilingual(input_list=field_contents, default_lang=default_lang)
            elif isinstance(field, str):
                multi_dict[field] = [convert_to_multilingual_dict(input_str=field_contents, default_lang=default_lang)]
            else:
                continue

        return multi_dict
    
    def convert_fields_to_literal(
        self,
        metadata_input_model: BaseModel | Dict[str, Any],
        default_lang: str = "no"
    ) -> Dict[str, Any]:
        """
        Converts multilingual fields in a DCAT Metadata Input Model to Norwegian multilingual Literals
        of the form {"no": "string"}
        """
        multi_dict = {}
        multilingual_fields = ["title", "name", "fullname", "description", "keyword"]
        nested_string_list_fields = ["subject_fields"]
        nested_dict_list_fields = ["datasets",]
        excluded_nested_raird_fields = ["unittypes", "variables"]  # Multiling. Literals are only for DCAT std, not RAIRD

        if isinstance(metadata_input_model, BaseModel):
            input_dict = metadata_input_model.model_dump(exclude_unset=True)
        else:
            input_dict = metadata_input_model

        # Convert string fields to Norwegian literal multilungual strings if needed
        for field, value in input_dict.items():
            if field in excluded_nested_raird_fields:
                continue
            if value is None:
                continue

            if isinstance(value, list) and value:
                if field in nested_string_list_fields:
                    multi_dict[field] = convert_list_to_multilingual_literals(
                        input_list=value, 
                        default_lang=default_lang,
                        nested_list=True
                    )
                elif field in nested_dict_list_fields:
                    multi_dict[field] = [
                        self.convert_fields_to_literal(item, default_lang=default_lang) \
                        for item in value
                    ]
                else:
                    multi_dict[field] = value

            elif (isinstance(value, str) or isinstance(value, dict)) and field in multilingual_fields:
                multi_dict[field] = convert_to_multilingual_literal(
                    input_str_dict=value, 
                    default_lang=default_lang
                )

            elif isinstance(value, dict):
                _m_dict = {}
                for k, v in value.items():
                    if k in multilingual_fields:
                        _m_dict[k] = convert_to_multilingual_literal(
                            input_str_dict=v, 
                            default_lang=default_lang
                        )
                    else:
                        _m_dict[k] = v
                multi_dict[field] = _m_dict

            elif isinstance(value, str):
                # Not in the multilingual_fields list
                multi_dict[field] = value
            else:
                continue

        return multi_dict
    
    def output_catalog_ttl(
        self,
        catalog_metadata: Dict[str, Any],
    ) -> str:
        try:
            catalog = self.build_catalog_metadata(catalog_metadata)
            self.include_datasets = False if not catalog.datasets else True
            ttl = catalog.to_rdf(include_datasets=self.include_datasets).decode('utf-8')
        except Exception as e:
            print(f"Error in building DCAT-AP-NO Catalog, most likely due to missing metadata fields -> {str(e)}")

        return ttl    

    def output_dataset_ttl(
        self,
        dataset_metadata: Dict[str, Any],      
    ) -> str:
        try:
            dataset = self.build_dataset_metadata(dataset_metadata)
            ttl = dataset.to_rdf().decode('utf-8')
        except Exception as e:
            print(f"Error in building DCAT-AP-NO Dataset, most likely due to missing metadata fields -> {str(e)}")

        return ttl
    
    def build_catalog_metadata(
        self,
        catalog_metadata: Dict[str, Any],            
    ) -> Catalog:
        # cat_obj, cat_metadata = self.get_catalog()
        # dsets = cat_obj.datasets
        catalog = self.create_catalog_metadata(**catalog_metadata)

        # if dsets:
        #     dsets_metadata = self.get_datasets(ds_objs=dsets)
        #     datasets = [self.create_dataset_metadata(**ds) for ds in dsets_metadata]
        #     catalog.datasets = datasets

            # dists = ds.distributions
            # for dist in dists:
            #     distribution = self.create_distribution(**dist)
            #     dataset.add_distribution(distribution)

        return catalog
    
    def build_dataset_metadata(
        self,
        dataset_metadata: Dict[str, Any],    
    ) -> Dataset:
        dataset = self.create_dataset_metadata(**dataset_metadata)

        return dataset

    # def get_catalog(
    #     self
    # ) -> Tuple[ModelType, Dict[str, Any]]:
    #     catalog = crud.catalog.get(self.db, self.catalog_id)
    #     if not catalog:
    #         show_error_response(
    #             status_code=status.HTTP_404_NOT_FOUND, 
    #             detail="Not found in the Database"
    #         )

    #     metadata = catalog.json_metadata

    #     return catalog, metadata

    # def get_dataset(
    #     self
    # ) -> Tuple[ModelType, Dict[str, Any]]:
    #     dataset = crud.dataset.get(self.db, self.dataset_id)
    #     if not dataset:
    #         show_error_response(
    #             status_code=status.HTTP_404_NOT_FOUND, 
    #             detail="Not found in the Database"
    #         )

    #     metadata = dataset.json_metadata

    #     return dataset, metadata
    
    # def get_datasets(
    #     self, 
    #     ds_objs: List[ModelType] = None
    # ) -> List[Dict[str, Any]]:
    #     metadata_list = [md.json_metadata for md in ds_objs]

    #     return metadata_list

    def create_catalog_metadata(
        self,
        *,
        identifier, 
        title, 
        description, 
        publisher = None, 
        contact_point = None,
        theme = None,
        keyword = None,
        datasets = None,
    ) -> Catalog:
        catalog = Catalog(identifier=identifier)

        catalog.dct_identifier = identifier
        catalog.title = title
        catalog.description = description
        catalog.publisher = self.create_publisher_metadata(**publisher) if publisher else None
        catalog.contactpoint = self.create_contact_metadata(**contact_point) if contact_point else None
        catalog.themes = theme
        catalog.keyword = keyword

        if datasets:
            dataset_list = [self.create_dataset_metadata(**ds) for ds in datasets]
            catalog.datasets = dataset_list

        return catalog

    def create_dataset_metadata(
        self,
        *,
        identifier,
        title,
        description,
        publisher = None,
        contact_point = None,
        theme = None,
        spatial = None,
        keyword = None,
    ) -> Dataset:
        dataset = Dataset(identifier=identifier)

        dataset.dct_identifier = identifier
        dataset.title = title
        dataset.description = description
        dataset.publisher =  self.create_publisher_metadata(**publisher) if publisher else None
        dataset.theme = theme
        dataset.contactpoint = self.create_contact_metadata(**contact_point)
        dataset.spatial = spatial
        dataset.keyword = keyword

        return dataset

    def create_distribution_metadata(
        self,
        *,
        identifier,
        access_url,
    ) -> Distribution:
        distribution = Distribution(identifier=identifier)
        distribution.access_URL = access_url

        return distribution
    
    def create_publisher_metadata(
        self,
        *,
        identifier,
        name = None,
        description = None,
        organization_id = None,
        type = None,
    ) -> Agent:
        publisher = Agent(identifier=identifier)
        publisher.identifier = identifier
        publisher.name = name
        publisher.organization_id = organization_id
        publisher.organization_type = type

        return publisher
    
    def create_contact_metadata(
        self,
        *,
        identifier,
        name = None,
        phone = None,
        mbox = None,
        url = None,
    ) -> Contact:
        contact = Contact(identifier=identifier)
        contact.identifier = identifier
        contact.name = name
        contact.telephone = phone
        contact.email = mbox
        contact.url = url

        return contact  
    

dcat_process = DCATProcess()
