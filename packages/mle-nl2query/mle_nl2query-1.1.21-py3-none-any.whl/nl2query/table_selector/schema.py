from pydantic import BaseModel, Field
from typing import List, Optional


class TableSelectorSchema(BaseModel):
    tables: Optional[List[str]] = Field(
        ..., description="List of tables related to given user query."
    )
    selected_reason: Optional[str] = Field(
        ...,
        description="Justification for the selected tables based on the user query.",
    )
