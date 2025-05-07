import json
import time
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.table_selector.schema import TableSelectorSchema
from nl2query.core.llm_models import get_llm
from nl2query.table_selector.prompts import get_table_selector_prompts


class TableSelector(BaseModule):
    """Concrete implementation of BaseModule for intent detection"""

    def __init__(
        self,
        system_prompt: str = None,
        pydantic_class: TableSelectorSchema = TableSelectorSchema,
        prompt: str = None,
        examples: str = None,
        table_info: str = None,
        metadata_file_path: str = None,
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
        self.table_info = table_info
        self.metadata_file_path = metadata_file_path  # Store metadata file path

        logger.info(f"Initialized IntentEngine with prompt: {system_prompt}")

    def load_metadata(self):
        """Load the metadata either from the given JSON file path or directly from a JSON string."""
        try:
            if isinstance(
                self.metadata_file_path, str
            ) and self.metadata_file_path.startswith("{"):
                # If the metadata_file_path is a JSON string
                logger.info("Directly using provided JSON metadata.")
                return json.loads(self.metadata_file_path)

            elif isinstance(self.metadata_file_path, str):
                # If it's a file path, load the metadata from the file
                logger.info(f"Loading metadata from file: {self.metadata_file_path}")
                with open(self.metadata_file_path, "r") as file:
                    metadata = json.load(file)
                return metadata

            else:
                logger.warning(
                    "Invalid metadata source provided. Expected a file path or a JSON string."
                )
                return {}

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            raise

    def get_metadata_for_selected_tables(self, selected_tables):
        """Select the corresponding metadata from the JSON based on selected tables."""
        if not selected_tables:
            logger.info("No tables selected, skipping metadata retrieval.")
            return {}

        metadata = self.load_metadata()
        selected_metadata = {}

        for table in selected_tables:
            if table is None:
                logger.debug("Encountered null in selected_tables, skipping.")
                continue

            if table in metadata:
                selected_metadata[table] = metadata[table]
            else:
                logger.warning(f"Metadata for table {table} not found.")

        return selected_metadata

    def escape_metadata_braces(self, metadata):
        """Recursively replace '{' with '{{' and '}' with '}}' in the metadata."""
        if isinstance(metadata, dict):
            return {
                key: self.escape_metadata_braces(value)
                for key, value in metadata.items()
            }
        elif isinstance(metadata, str):
            return metadata.replace("{", "{{").replace("}", "}}")
        else:
            return metadata

    def run(self, state):
        """Process the state and return intent JSON"""
        try:
            start_time = time.time()
            self.model_type = state.get("model_type", "openai")
            self.model_name = state.get("model_name", "gpt-4o")
            self.temperature = state.get("temperature", 0.01)
            self.query = state["query"]

            prompt = get_table_selector_prompts(self.prompt, self.table_info)

            prompt = ChatPromptTemplate.from_messages(
                [("system", prompt), ("human", "{query}")]
            )

            llm = get_llm(
                model_type=self.model_type,
                model_name=self.model_name,
                temperature=self.temperature,
            )
            structured_llm = llm.with_structured_output(self.pydantic_class)
            few_shot_structured_llm = prompt | structured_llm

            response = few_shot_structured_llm.invoke({"query": self.query})

            selected_table = response.dict()["tables"]
            selected_table_reason = response.dict()["selected_reason"]

            logger.info(f"Selected tables:{selected_table}")
            logger.info(f"Selected reason:{selected_table_reason}")
            state["selected_tables"] = selected_table
            if not selected_table: 
                raise ValueError("Query is not bound within the given table metadata.")

            state["selected_table_reason"] = selected_table_reason

            selected_metadata = self.get_metadata_for_selected_tables(selected_table)
            logger.info(f"Selected metadata: {selected_metadata}")

            # metadata = json.loads(selected_metadata)

            # escaped_metadata_str = metadata_str.replace("{", "{{").replace("}", "}}")

            state["metadata"] = selected_metadata

            state["raw_messages"].append(
                {"role": "table_selector", "content": response}
            )
            formatted_message = {"role": "user", "content": state["query"]}
            state["messages"].append(formatted_message)
            end_time = time.time()
            response_time = end_time - start_time
            state["table_selector_response_time"] = response_time
            logger.info(f"Table selector processing time: {response_time}")

            return state, selected_table

        except Exception as e:
            logger.error(f"Error processing intent: {e}")
            raise
