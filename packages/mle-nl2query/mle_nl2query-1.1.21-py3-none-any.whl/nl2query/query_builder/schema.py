from pydantic import BaseModel, Field
from typing import Optional


class QueryBuilderSchema(BaseModel):
    output_query: Optional[str] = Field(
        ..., description="Valid SQL query based on given reframed query or intent json"
    )
