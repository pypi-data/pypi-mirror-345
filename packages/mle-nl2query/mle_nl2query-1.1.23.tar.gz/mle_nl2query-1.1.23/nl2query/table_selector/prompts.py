def get_table_selector_prompts(prompt=None, tables_info=None):
    """Function to generate prompts for the pre-filtering engine."""

    if tables_info is None:
        tables_info = ["customers", "products", "order", "order_items"]

    if not prompt:
        prompts = f"""
        Task: Analyze the provided natural language query to determine which tables in the database it references.
        List only the relevant tables from the provided list of tables without giving any explanations or reasoning.

        Input:
        1. Natural Language Query: `query`
        2. **List of Available Tables:**
        {tables_info}

        Output Requirement:
        Provide a list of tables from the provided list that are referenced in the natural language query only if you are sure of it.

        **Guidelines:**
        1. Make sure to list only the relevant tables from the available list.
        2. If no tables are related to the given query, return an empty list.

        Expected Output Format:
        ["ReferencedTable1", "ReferencedTable2", ...]
        (Continue listing all relevant tables identified.)
        """
    else:
        prompts = f"{prompt} \n\n **Tables_info**{tables_info}"

    return str(prompts)
