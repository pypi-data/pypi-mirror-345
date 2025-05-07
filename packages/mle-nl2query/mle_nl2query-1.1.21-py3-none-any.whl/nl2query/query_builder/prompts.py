QUERY_BUILDER_PROMPT = (
    "You are an expert SQL query generator. Your task is to convert a natural language query or an intent JSON "
    "into a syntactically correct SQL query based on the provided schema. "
    "Make sure to prepend the schema name to the table names, i.e., format as SCHEMA_NAME.TABLE_NAME."
)

EXAMPLE_WITH_INTENT_JSON = """
Example:
Natural language query: "What’s the total sales for 2023?"
intent_JSON: {{"intent": "aggregate", "entities": [{{"field": "total", "value": null}}, {{"field": "date", "value": "2023"}}], "operation": "sum"}}
SQL Query: "SELECT SUM(total) FROM SALES_SCHEMA.SALES WHERE date = '2023' LIMIT 5"
"""

EXAMPLE_WITHOUT_INTENT_JSON = """
Example:
Natural language query: "What’s the total sales for 2023?"
SQL Query: "SELECT SUM(total) FROM SALES_SCHEMA.SALES WHERE date = '2023' LIMIT 5"
"""

GUIDELINES = """
Guidelines:
- Limit results to 5 unless specified otherwise.
- Return only the query as plain text, no additional text or JSON.
- Include the schema prefix (e.g., SCHEMA_NAME.TABLE_NAME) in the SQL query.
"""


def get_query_builder_prompt(prompt=None, examples=None, schema_name=None):
    """Generate a prompt for building an SQL query based on the state."""
    prompt_parts = []
    base_prompt = prompt if prompt else QUERY_BUILDER_PROMPT
    prompt_parts.append(base_prompt)

    examples_text = "\n".join(examples) if examples else EXAMPLE_WITHOUT_INTENT_JSON
    prompt_parts.append(f"Examples:\n{examples_text}")

    if schema_name:
        prompt_parts.append(
            f"Schema name provided: {schema_name}. Make sure to use the schema prefix for all table names."
        )
    if not prompt:
        prompt_parts.append(GUIDELINES)

    return "\n\n".join(prompt_parts)
