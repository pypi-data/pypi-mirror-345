import time
import re
import json

from typing import Mapping
from loguru import logger
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.query_validator.schema import QueryValidatorSchema
from nl2query.core.llm_models import get_llm
from nl2query.query_validator.prompts import get_query_validator_prompt


class QueryValidator(BaseModule):
    """Concrete implementation of BaseModule for intent detection"""

    def __init__(
        self,
        system_prompt: str = None,
        pydantic_class: QueryValidatorSchema = QueryValidatorSchema,
        prompt: str = None,
        examples: str = None,
        schema_mapping_path: str = "data/input/schema_mapping.json",
        *args,
        **kwargs,
    ):
        super().__init__(
            system_prompt=system_prompt,
            pydantic_class=pydantic_class,
            examples=examples,
            *args,
            **kwargs,
        )
        self.prompt = prompt
        self.examples = examples
        self.pydantic_class = pydantic_class
        self.schema_mapping_path = schema_mapping_path

        logger.info(f"Initialized IntentEngine with prompt: {system_prompt}")

    def load_schema_mapping(self, path: str | Path) -> Mapping[str, str]:
        """Load a JSON file that maps table names to their desired schema names."""
        with open(path, "r") as f:
            return json.load(f)

    def replace_schema_prefix_in_query(
        self, query: str, schema_map: Mapping[str, str]
    ) -> str:
        """
        For every prefix.table or standalone table occurrence in the SQL, if `table` exists in schema_map,
        replace it with `schema_map[table] + "." + table`.
        """
        # Pattern to match both prefixed (schema.table) and standalone (table) names
        pattern = re.compile(r"\b(?:(?P<prefix>\w+)\.)?(?P<table>\w+)\b")

        def _repl(m: re.Match) -> str:
            table = m.group("table")
            # prefix = m.group("prefix")
            if table in schema_map:
                # If the table is in the mapping, always use the mapped schema
                return f"{schema_map[table]}.{table}"
            return m.group(0)  # Return original text if table not in mapping

        return pattern.sub(_repl, query)

    def run(self, state):
        """Process the state and return intent JSON"""
        try:
            start_time = time.time()
            model_type = state.get("model_type", "openai")
            model_name = state.get("model_name", "gpt-4o")
            temperature = state.get("temperature", 0.01)
            # if state["query_reframer_yn"]:
            #     query = state["reframed_query"]
            # else:
            #     query = state["query"]

            prompt = get_query_validator_prompt(self.prompt)

            prompt = ChatPromptTemplate.from_messages(
                [("system", prompt), ("human", "{initial_query}")]
            )

            llm = get_llm(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )
            structured_llm = llm.with_structured_output(self.pydantic_class)
            few_shot_structured_llm = prompt | structured_llm
            initial_query = state["initial_query"]
            response = few_shot_structured_llm.invoke({"initial_query": initial_query})
            validated_query = response.dict()["validated_query"]

            schema_map = self.load_schema_mapping(self.schema_mapping_path)
            final_query = self.replace_schema_prefix_in_query(
                validated_query, schema_map
            )

            state["validated_query"] = final_query

            logger.info(f"Query after validation: {validated_query}")
            state["raw_messages"].append(
                {"role": "validated_query", "content": response}
            )

            system_message = {"role": "ai", "content": validated_query}
            state["messages"].append(system_message)

            end_time = time.time()
            response_time = end_time - start_time
            state["query_validator_response_time"] = response_time
            logger.info(f"Query validator processing time: {response_time}")

            return state, final_query

        except Exception as e:
            logger.error(f"Error processing intent: {e}")
            raise
