from pydantic import BaseModel, Field
from typing import Optional


class QueryValidatorSchema(BaseModel):
    validated_query: Optional[str] = Field(
        None,
        description="A validated Snowflake SQL query string without syntax or logical errors.",
    )
