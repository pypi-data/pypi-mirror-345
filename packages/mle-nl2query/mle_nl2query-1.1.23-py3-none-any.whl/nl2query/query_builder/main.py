import json
import time

from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.query_builder.schema import QueryBuilderSchema
from nl2query.core.llm_models import get_llm
from nl2query.query_builder.prompts import get_query_builder_prompt


class QueryBuilder(BaseModule):
    """Concrete implementation of BaseModule for intent detection"""

    def __init__(
        self,
        system_prompt: str = None,
        pydantic_class: QueryBuilderSchema = QueryBuilderSchema,
        examples: str = None,
        schema_name: str = None,
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

        self.prompt = system_prompt
        self.examples = examples
        self.pydantic_class = pydantic_class
        self.schema_name = schema_name

        logger.info(f"Initialized IntentEngine with prompt: {system_prompt}")

    def run(self, state):
        """Process the state and return intent JSON"""
        try:
            start_time = time.time()
            model_type = state.get("model_type", "openai")
            model_name = state.get("model_name", "gpt-4-1106-preview")
            temperature = state.get("temperature", 0.01)
            if state["query_reframer_yn"]:
                query = state["reframed_query"]
            else:
                query = state["query"]

            if state["intent_yn"]:
                intent_json = state["intent_json"]

            # TODO: Add both examples with 'intent_json' and 'reframed_query'
            # You can modify this as needed to add examples from your use case.

            prompt = get_query_builder_prompt(query, self.prompt, self.schema_name)

            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system", f"{prompt}"),
                    ("human", "{query}"),
                    ("system", "{intent_json}"),
                ]
            )
            llm = get_llm(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )

            structured_llm = llm.with_structured_output(self.pydantic_class)
            few_shot_structured_llm = prompt_template | structured_llm

            response = few_shot_structured_llm.invoke(
                {"query": query, "intent_json": json.dumps(intent_json)}
            )
            response = response.dict()["output_query"]

            initial_query = response
            state["initial_query"] = initial_query
            state["raw_messages"].append({"role": "initial_query", "content": response})

            logger.info(f"Initial query from query builder module: {initial_query}")
            end_time = time.time()
            response_time = end_time - start_time
            state["query_builder_processing_time"] = response_time

            logger.info(f"Query Builder processing time: {response_time:.4f} seconds")

            return state, response

        except Exception as e:
            logger.error(f"Error processing intent: {e}")
            raise
