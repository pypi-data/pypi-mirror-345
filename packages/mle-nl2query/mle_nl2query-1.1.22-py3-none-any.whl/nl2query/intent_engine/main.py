import time
import json

from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.intent_engine.schema import IntentJsonSchema
from nl2query.core.llm_models import get_llm
from nl2query.intent_engine.prompts import get_intent_prompt


class IntentEngine(BaseModule):
    """Concrete implementation of BaseModule for intent detection"""

    def __init__(
        self,
        system_prompt: str,
        pydantic_class: IntentJsonSchema = IntentJsonSchema,
        metadata: str = None,
        examples: str = None,
        config: str = None,
        intent_structure: str = None,
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
        self.intent_structure = intent_structure
        self.config = config
        self.pydantic_class = pydantic_class

        logger.info(f"Initialized IntentEngine with prompt: {system_prompt}")

    def run(self, state):
        """Process the state and return intent JSON"""
        try:
            start_time = time.time()
            self.metadata = state["metadata"]  # TODO remove
            model_type = state.get("model_type", "openai")
            model_name = state.get("model_name", "gpt-4o")
            temperature = state.get("temperature", 0.01)

            if state["query_reframer_yn"]:
                self.query = state["reframed_query"]
            else:
                self.query = state["query"]

            prompt = get_intent_prompt(
                self.prompt, self.examples, self.metadata, self.intent_structure
            )

            prompt = ChatPromptTemplate.from_messages(
                [("system", prompt), ("human", "{query}")]
            )

            llm = get_llm(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )
            structured_llm = llm.with_structured_output(self.pydantic_class)
            few_shot_structured_llm = prompt | structured_llm

            response = few_shot_structured_llm.invoke({"query": self.query})
            intent_json = response.dict()["intent_json"]
            logger.info(f"Intent JSON: {intent_json}")
            if "error_message" in intent_json:
                err = intent_json["error_message"]
                raise Exception(f"Intent Engine Error: {err}")

            if isinstance(intent_json, str):
                intent_json_rbac = json.loads(intent_json)
            elif isinstance(intent_json, dict):
                intent_json_rbac = intent_json
            else:
                raise TypeError(f"Unexpected type for intent_json: {type(intent_json)}")

            operation = intent_json_rbac.get("operation")
            if operation != "read":
                raise Exception(
                    f"Intent Engine Error: Operation {operation} not supported"
                )
            else:
                state["intent_json"] = intent_json
                logger.info(f"Intent JSON: {intent_json}")
                state["raw_messages"].append(
                    {"role": "intent_json", "content": response}
                )
                end_time = time.time()
                response_time = end_time - start_time
                state["intent_engine_processing_time"] = response_time

                logger.info(
                    f"Intent engine processing time: {response_time:.4f} seconds"
                )

                return state, state["intent_json"]

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            return {"error": "Invalid JSON response from LLM"}
        except Exception as e:
            logger.error(f"Error processing intent: {e}")
            raise
