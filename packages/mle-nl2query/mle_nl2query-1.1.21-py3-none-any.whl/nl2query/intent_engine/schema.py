from pydantic import BaseModel, Field
from typing import Dict, Optional


class IntentJsonSchema(BaseModel):
    """Schema for the intent json"""

    intent_json: Optional[Dict] = Field(
        ...,
        description="A dictionary representing the user's query identified intent that includes the implicitly mentioned Snowflake query fields from the given schema.",
    )
