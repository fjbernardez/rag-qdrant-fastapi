from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    qdrant_url: str
    qdrant_collection: str
    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    embedding_batch_size: int = Field(
        default=64,
        gt=0,
        validation_alias="EMBEDDING_BATCH_SIZE",
    )


settings = Settings()
