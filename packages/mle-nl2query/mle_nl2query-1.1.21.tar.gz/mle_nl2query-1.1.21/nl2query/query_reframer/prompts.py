QUERY_REFRAMER_WITH_METADATA_PROMPT = (
    "You are an expert SQL query generator. Use the provided config mapping, metadata, and examples "
    "to reframe the user's natural language query into a precise reframed query with detailed information."
)

QUERY_REFRAMER_WITH_CONFIG_PROMPT = (
    "You are an expert SQL query generator. Use the provided config mapping and examples "
    "to reframe the user's natural language query into a precise reframed query with detailed information."
)

QUERY_REFRAMER_WITH_METADATA_EXAMPLES = """
**Examples**
Example 1:
    query: What is the average sales today?
    reframed_query: What is the average of the 'total' column (sales) in the 'sales' table for transactions occurring today, considering the 'date' column?

Example 2:
    query: Give me top customers by sales.
    reframed_query: Identify the top customer IDs from the 'sales' table, ordered by the total sum of the 'total' column (sales), including details on customer name and total sales amount.
"""

QUERY_REFRAMER_WITH_CONFIG_EXAMPLES = """
**Examples**
Example 1:
    query: What is the average sales today?
    reframed_query: What is the average of the 'total' column (sales) in 'sales' table for transactions occurring today, considering the 'date' column?

Example 2:
    query: Give me top customers by sales.
    reframed_query: Identify the top customer IDs from the 'sales' table, ordered by the total sum of the 'total' column (sales), including details on customer name and total sales amount.
"""

# New config mapping prompt and examples for SQL sales queries
CONFIG_MAPPING_PROMPT_SALES = """You are an expert in mapping natural language terms to SQL database fields. Given the user's query, map the key terms or technical jargons to their corresponding table columns or conditions based on the provided config mapping. Return the mapping as a JSON object.
"""

CONFIG = """
      "technical_jargon": {{
        "customers": [
          "client details",
          "user information",
          "account holder data"
        ],
        "orders.status = 'pending'": [
          "unprocessed orders",
          "awaiting fulfillment",
          "incomplete transactions"
        ],
        "order_items.quantity > 0": [
          "active line items",
          "purchased products"
        ],
        "products.stock_quantity": [
          "inventory levels",
          "available stock"
        ],
        "orders.order_date": [
          "transaction timestamp",
          "purchase date"
        ],
        "order_items.price * order_items.quantity": [
          "line item total",
          "product revenue"
        ]
      }}
"""

CONFIG_MAPPING_EXAMPLES_SALES = """
Example 1:
user_query: What is the total sales amount for this month?
mapping_output:
{{
    "total sales amount": "sales.total"
}}

Example 2:
user_query: Who are my top 5 customers by revenue last quarter?
mapping_output:
{{
    "top 5 customers": "ORDER BY SUM(sales.total) DESC LIMIT 5",
    "revenue": "sales.total"
}}
"""


def get_reframed_query_with_config_prompt(
    # query: str,
    # config: str,
    query_reframer_with_config_prompt: str = None,
    query_reframer_with_config_examples: str = None,
) -> str:
    query_reframer_prompt = []

    config_prompt = (
        query_reframer_with_config_prompt
        if query_reframer_with_config_prompt
        else QUERY_REFRAMER_WITH_CONFIG_PROMPT
    )
    query_reframer_prompt.append(config_prompt)

    if query_reframer_with_config_examples:
        query_reframer_prompt.append(
            f"Examples:\n{query_reframer_with_config_examples}"
        )
    else:
        query_reframer_prompt.append(
            f"Examples:\n{QUERY_REFRAMER_WITH_CONFIG_EXAMPLES}"
        )
    # escaped_config = str(config).replace("{", "{{").replace("}", "}}")
    # query_reframer_prompt.append("\n**mapping_output**:\n" + escaped_config)

    if not query_reframer_with_config_prompt:
        query_reframer_prompt.append(
            "Reframe the `query` into a precise SQL query and return it as plain text."
        )

    return "\n\n".join(query_reframer_prompt)


def get_reframed_query_with_metadata_prompt(
    query: str,
    metadata: str,
    query_reframer_with_metadata_prompt: str = None,
    query_reframer_with_metadata_examples: str = None,
) -> str:
    """Generate a prompt for reframing a query using database configuration and metadata."""
    query_reframer_prompt = []

    metadata_prompt = (
        query_reframer_with_metadata_prompt
        if query_reframer_with_metadata_prompt
        else QUERY_REFRAMER_WITH_METADATA_PROMPT
    )
    query_reframer_prompt.append(metadata_prompt)

    query_reframer_prompt.append(f"**Metadata:**\n{metadata}")

    if query_reframer_with_metadata_examples:
        query_reframer_prompt.append(
            f"Examples:\n{query_reframer_with_metadata_examples}"
        )
    else:
        query_reframer_prompt.append(
            f"Examples:\n{QUERY_REFRAMER_WITH_METADATA_EXAMPLES}"
        )

    query_reframer_prompt.append(f"Given the query: '{query}'")

    if not query_reframer_with_metadata_prompt:
        query_reframer_prompt.append(
            "Reframe the `query` into a precise SQL query and return it as plain text."
        )

    prompt = "\n\n".join(query_reframer_prompt)
    return prompt


def get_config_mapping_prompt(
    config: str,
    config_mapping_prompt: str = None,
    config_mapping_examples: str = None,
) -> str:
    """Generate a prompt for mapping query terms to SQL database fields."""
    config_mapping_prompt_list = []

    prompt = (
        config_mapping_prompt if config_mapping_prompt else CONFIG_MAPPING_PROMPT_SALES
    )
    config_mapping_prompt_list.append(prompt)
    escaped_config = str(config).replace("{", "{{").replace("}", "}}")
    config_mapping_prompt_list.append("Config mapping:\n" + escaped_config)

    if config_mapping_examples:
        config_mapping_prompt_list.append(f"**Examples:**\n{config_mapping_examples}")
    else:
        config_mapping_prompt_list.append(
            f"**Examples:**\n{CONFIG_MAPPING_EXAMPLES_SALES}"
        )

    if not config_mapping_prompt:
        config_mapping_prompt_list.append("Given the query:")
        config_mapping_prompt_list.append(
            "Map the key terms in the `query` to their corresponding SQL table columns or conditions and return the mapping as a JSON object with a key 'mapping_output'. "
            "The JSON object should have a field named 'mapping_output' that contains the key-value pairs."
        )
    prompt = "\n\n".join(config_mapping_prompt_list)
    return prompt
