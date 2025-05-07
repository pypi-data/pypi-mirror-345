import time
import json
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.query_reframer.schema import (
    QueryReframerWithConfigSchema,
    QueryReframerConfigSchema,
    QueryReframerWithMetadataSchema,
)
from nl2query.core.llm_models import get_llm
from nl2query.query_reframer.prompts import (
    get_reframed_query_with_config_prompt,
    get_reframed_query_with_metadata_prompt,
    get_config_mapping_prompt,
)


class QueryReframer(BaseModule):
    """Concrete implementation of BaseModule for query reframing with conditional config, metadata, and examples"""

    def __init__(
        self,
        config_mapping_prompt: str = None,
        query_reframer_with_config_prompt: str = None,
        query_reframer_with_metadata_prompt: str = None,
        pydantic_class: QueryReframerWithConfigSchema = QueryReframerWithConfigSchema,
        query_reframer_with_config_examples: str = None,
        config_mapping_example: str = None,
        query_reframer_with_metatdata_examples: str = None,
        config: str = None,
        metadata_file_path: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            pydantic_class=pydantic_class,
            examples=query_reframer_with_config_examples,
            *args,
            **kwargs,
        )
        self.metadata_file_path = metadata_file_path
        self.query = ""
        self.rephrased_query = ""
        self.pydantic_class = pydantic_class
        self.config_mapping_prompt = config_mapping_prompt
        self.query_reframer_with_config_prompt = query_reframer_with_config_prompt
        self.query_reframer_with_metadata_prompt = query_reframer_with_metadata_prompt
        self.query_reframer_with_metadata_examples = (
            query_reframer_with_metatdata_examples
        )
        self.query_reframer_with_config_examples = query_reframer_with_config_examples
        self.config_mapping_example = config_mapping_example
        self.config = config

    def get_previous_msg(self, state):
        previous_messages = ""

        if len(state["messages"]) > 2:
            messages_to_process = (
                state["messages"][-10:]
                if len(state["messages"]) > 10
                else state["messages"]
            )
            for message in messages_to_process:
                role = message["role"]
                content = message["content"]
                if role == "user":
                    previous_messages += f"user: {content}\n"
                elif role == "ai":
                    previous_messages += f"ai: {content}\n"

        previous_messages = str(previous_messages)
        previous_messages = previous_messages.replace("{", "{{").replace("}", "}}")

        return previous_messages

    def load_metadata(self):
        """Load the metadata from the given JSON file path."""
        try:
            with open(self.metadata_file_path, "r") as file:
                metadata = json.load(file)
            return metadata
        except Exception as e:
            logger.error(
                f"Error loading metadata from file {self.metadata_file_path}: {e}"
            )
            raise

    def convert_metadata(self, metadata):
        lines = []
        for table_name, fields in metadata.items():
            lines.append(f"Table: {table_name}")

            table_desc = fields.get("description")
            if table_desc:
                lines.append(f"  Description: {table_desc}\n")

            for field_name, field_info in fields.items():
                if field_name == "description":
                    continue
                data_type = field_info.get("type", "")
                desc = field_info.get("description", "")
                lines.append(f"  {field_name}: {data_type} => {desc}")
            lines.append("")
        return "\n".join(lines)

    def run(self, state):
        """Core logic to reframe the query into an SQL query based on config, metadata, and examples"""
        start_time = time.time()
        # self.metadata = self.load_metadata()
        self.metadata = self.convert_metadata(state["metadata"])
        state["metadata"] = self.metadata
        self.model_type = state.get("model_type", "openai")
        self.model_name = state.get("model_name", "gpt-4-1106-preview")
        self.temperature = state.get("temperature", 0.01)
        self.query = state["query"]

        self.previous_messages = self.get_previous_msg(state)

        if state["query_reframer_metadata_yn"]:
            self.query_reframer_with_metadata_prompt = (
                self.query_reframer_with_metadata_prompt
            )
            self.query_reframer_with_metadata_examples = (
                self.query_reframer_with_metadata_examples
            )
        elif state["query_reframer_config_yn"]:
            self.query_reframer_with_config_prompt = (
                self.query_reframer_with_config_prompt
            )
            self.query_reframer_with_config_examples = (
                self.query_reframer_with_config_examples
            )
        else:
            self.query_reframer_examples = self.examples

        if state["query_reframer_config_yn"]:
            # Get config mapping prompt
            prompt_text = get_config_mapping_prompt(
                self.config,
                self.config_mapping_prompt,
                self.config_mapping_example,
            )

            if isinstance(prompt_text, dict):
                prompt_text = str(prompt_text.get("prompt", ""))

            prompt_template = ChatPromptTemplate.from_messages(
                [("system", prompt_text), ("human", "{query}")]
            )

            llm = get_llm(
                model_type=self.model_type,
                model_name=self.model_name,
                temperature=self.temperature,
            )
            structured_llm = llm.with_structured_output(QueryReframerConfigSchema)

            few_shot_structured_llm = prompt_template | structured_llm

            query = (
                f"Previous messages: {self.previous_messages} \n\n {self.query}"
                if self.previous_messages
                else self.query
            )
            logger.info(f"Input for config mapping: {query}")

            response = few_shot_structured_llm.invoke({"query": query})
            result = response.dict()
            mapping_output = result["mapping_output"]
            state["mapping_output"] = mapping_output
            state["raw_messages"].append(
                {"role": "mapping_output", "content": mapping_output}
            )

            logger.info(f"Mapping Config: {mapping_output}")

            if not mapping_output or mapping_output == {}:
                logger.info("Mapping output is empty, skipping reframing with config.")
            else:
                prompt = get_reframed_query_with_config_prompt(
                    # mapping_output,
                    self.query_reframer_with_config_prompt,
                    self.query_reframer_with_config_examples,
                )
                prompt_template = ChatPromptTemplate.from_messages(
                    [
                        ("system", prompt_text),
                        ("human", "query: {query} \n\n mapping_json: {mapping_json}"),
                    ]
                )
                llm = get_llm(
                    model_type=self.model_type,
                    model_name=self.model_name,
                    temperature=self.temperature,
                )
                structured_llm = llm.with_structured_output(
                    QueryReframerWithConfigSchema
                )

                few_shot_structured_llm = prompt_template | structured_llm
                input_data = {
                    "query": self.query,
                    "mapping_json": json.dumps(mapping_output),
                }
                response = few_shot_structured_llm.invoke(input=input_data)
                # response = few_shot_structured_llm.invoke({"query": self.query})
                reframed_query = response.dict()["reframed_query"]

                logger.info(f"Reframed query with config: {reframed_query}")
                state["reframed_query_with_config"] = reframed_query
                state["reframed_query"] = reframed_query

        if state["query_reframer_metadata_yn"]:
            if not mapping_output or mapping_output == {}:
                logger.info("Mapping output is empty, skipping reframing with config.")
                state["reframed_query_with_config"] = None
                state["reframed_query"] = None
                query = state["query"]

            else:
                query = (
                    state["reframed_query_with_config"]
                    if state.get("query_reframer_config_yn")
                    and state.get("reframed_query_with_config") is not None
                    else state["query"]
                )

            prompt = get_reframed_query_with_metadata_prompt(
                query,
                self.metadata,
                self.query_reframer_with_metadata_prompt,
                self.query_reframer_with_metadata_examples,
            )

            if isinstance(prompt, dict):
                prompt = str(prompt.get("prompt", ""))

            query = (
                f"Previous messages: {self.previous_messages} \n\n {self.query}"
                if self.previous_messages
                else query
            )
            logger.info(f"Input for query reframer: {query}")

            prompt = ChatPromptTemplate.from_messages(
                [("system", prompt), ("human", "{query}")]
            )

            llm = get_llm(
                model_type=self.model_type,
                model_name=self.model_name,
                temperature=self.temperature,
            )
            structured_llm = llm.with_structured_output(
                QueryReframerWithMetadataSchema,
            )
            few_shot_structured_llm = prompt | structured_llm

            response = few_shot_structured_llm.invoke({"query": query})
            rephrased_query = response.dict()["reframed_query"]
            state["reframed_query_with_metadata"] = rephrased_query
            state["reframed_query"] = rephrased_query

            logger.info(f"Reframed query with metadata: {rephrased_query}")

            state["raw_messages"].append(
                {"role": "rephrased_query", "content": self.rephrased_query}
            )
            end_time = time.time()
            response_time = end_time - start_time
            state["query_reframer_response_time"] = response_time
            logger.info(f"Query reframer processing time: {response_time}")

        return state, state["reframed_query"]
