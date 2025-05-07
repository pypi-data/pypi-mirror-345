from pydantic import BaseModel, Field
from typing import Dict, Optional


class QueryReframerWithConfigSchema(BaseModel):
    reframed_query: Optional[str] = Field(
        ...,
        description="Reframed natural language query incorporating Snowflake field names or descriptions from given *mapping_json*. Replace original user terms with mapped fields in the generated query, include inline annotations. Donot return null or empty string.",
    )


class QueryReframerWithMetadataSchema(BaseModel):
    reframed_query: Optional[str] = Field(
        ...,
        description="Reframed natural language query that integrates Snowflake field names or descriptions derived from the provided *tables metadata*. The query must utilize the field descriptions from the metadata to replace original terms, ensuring alignment with the table's structure.",
    )


class QueryReframerConfigSchema(BaseModel):
    """Schema for the key point."""

    mapping_output: Optional[Dict] = Field(
        ..., description="Config mapping of technical terms to datatbase schema."
    )
