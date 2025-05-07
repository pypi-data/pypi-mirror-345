INTENT_ENGINE_PROMPT = (
    "You are an expert at converting natural language queries into structured intent JSON. "
    "Your task is to analyze the provided natural language query and output a structured `intent_JSON` "
    "that identifies the intent and key entities involved."
)

INTENT_STRUCTURE = """
        The structure of the expected `intent_JSON` should be:
            - "intent": (String) The primary action or purpose of the query (e.g., "search", "aggregate", "filter").
            - "entities": (Array of Object) Key entities mentioned in the query with their fields:
            - "field": (String) The schema field referenced.
            - "value": (String, optional) Specific value if mentioned.
            - "operation": (String) The type of operation (e.g., "select", "count", "sum").

            Example:
            Query: "What’s the total sales for 2023?"
            intent_JSON: {{
            "intent": "aggregate",
            "entities": [
                {{"field": "total", "value": null}},
                {{"field": "date", "value": "2023"}}
            ],
            "operation": "sum"
        }}
"""

GUIDELINES = """
Guidelines:
- Identify the main intent of the query (e.g., search, count, aggregate).
- Map any mentioned fields to the schema; if a field isn’t in the schema, include an error in the JSON.
- Return only the `intent_JSON` in valid JSON format, no additional text.
"""


def get_intent_prompt(
    prompt=None,
    examples=None,
    metadata=None,
    intent_structure=None,
    guidelines=None,
    *args,
    **kwargs,
):
    """Generate a simple prompt for intent detection based on the state"""

    intent_engine_prompt = [prompt] if prompt else [INTENT_ENGINE_PROMPT]

    intent_engine_prompt.append(f"**Schema Details**:\n{metadata}")
    intent_engine_prompt.append(
        intent_structure if intent_structure else INTENT_STRUCTURE
    )

    if examples:
        intent_engine_prompt.append(examples)

    intent_engine_prompt.append(guidelines if guidelines else GUIDELINES)
    return "\n\n".join(intent_engine_prompt)
