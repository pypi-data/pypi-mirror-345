from typing import Any, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "kudaflib"

    # KUDAF URLs
    KUDAF_METADATA_BACKEND_BASE_URLS: Dict[str, Any] = {
        "DEV": "http://localhost:8000/",
        "STAGING": 'https://kudaf-metadata-staging.sokrates.edupaas.no/', # New realm as of 26/2/25 (Platon, Hogne)
        "PRODUCTION": 'https://kudaf-metadata.paas2.uninett.no/',   # TODO: Updata this when we have a production realm
    }
    KUDAF_METADATA_BACKEND_URLS: Dict[str, Any] = {
        "catalog": "api/v1/catalogs/",
        "dataset": "api/v1/datasets/",
        "variable": "api/v1/variables/",
        "variables_metadata": "api/v1/variables/metadata/",
        "unit_type": "api/v1/unittypes/",
        "unit_type_catalog": "api/v1/unittypes/catalog/",
    }

    model_config = SettingsConfigDict(
        case_sensitive=True,
    )


settings = Settings()
