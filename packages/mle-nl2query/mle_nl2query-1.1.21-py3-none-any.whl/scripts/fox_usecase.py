import uuid
from nl2query.agent.graph import NL2QueryGraph
from nl2query.agent.state import State
from nl2query.intent_engine.main import IntentEngine
from nl2query.query_reframer.main import QueryReframer
from nl2query.table_selector.main import TableSelector
from nl2query.query_builder.main import QueryBuilder
from nl2query.query_validator.main import QueryValidator
from nl2query.query_executor.main import QueryExecutor
from nl2query.intent_ambiguity_handler.main import IntentAmbiguityHandler
from dotenv import load_dotenv
from examples.utils import load_json_file, load_txt_file
from loguru import logger


# Define QueryCacher and QueryCacheNode
class QueryCacher:
    def run(self, state):
        logger.info("Query cacher running")
        return state


class QueryCacheNode:
    def __init__(self, query_cache=None):
        self._query_cache = query_cache

    def __call__(self, state, **kwargs):
        try:
            logger.info("I am here at Query cache module: Not implemented yet.")
            state["state_id"] = 11
            self._query_cache.run(state)
            return state
        except Exception as e:
            raise Exception(f"Error at QueryCacheNode: {e}")


query_cache_instance = QueryCacher()


# Define FoxFramework
class FoxFramework(NL2QueryGraph):
    def __init__(self, config_file_path: str = "config.yaml", **kwargs):
        super().__init__(config_file_path=config_file_path, **kwargs)

    def _setup_nodes(self):
        super()._setup_nodes()
        if "query_cache_node" not in self.graph.nodes:
            self.graph.add_node(
                "query_cache_node", QueryCacheNode(query_cache=query_cache_instance)
            )
            logger.info("Added node: query_cache_node")

    def _setup_edges(self):
        super()._setup_edges()
        self.remove_edge("query_reframer_node", "intent_engine_node")
        self.add_conditional_edge(
            "query_reframer_node",
            condition=lambda state: "query_cache_node"
            if state.get("use_cache", True)
            else "query_builder_node",
            targets={"query_cache_node", "query_builder_node", "last_node"},
        )
        self.add_conditional_edge(
            "query_cache_node",
            condition=lambda state: "intent_engine_node"
            if state.get("proceed_to_intent", True)
            else "last_node",
            targets={"intent_engine_node", "last_node"},
        )


class FoxState(State, total=False):
    followup_query: str = None


if __name__ == "__main__":
    load_dotenv()
    # "intent_ambiguity_handler_node",
    interrupt_before = ["query_reframer_node"]
    table_info = load_txt_file("examples/example_fox/input/table_metadata.txt")
    table_selector_prompt = load_txt_file(
        "examples/example_fox/input/table_selector_prompt.txt"
    )
    table_selector_instance = TableSelector(
        prompt=table_selector_prompt,
        table_info=table_info,
        metadata_file_path="examples/example_fox/input/tables_metadata.json",
    )

    # Load prompts and configs
    config_mapping_prompt = load_txt_file(
        "examples/example_fox/input/config_mapping_prompt.txt"
    )
    query_reframer_with_config_prompt = load_txt_file(
        "examples/example_fox/input/query_reframer_with_config_prompt.txt"
    )
    query_reframer_with_metadata_prompt = load_txt_file(
        "examples/example_fox/input/query_reframer_with_metadata_prompt.txt"
    )
    query_reframer_with_config_examples = load_txt_file(
        "examples/example_fox/input/query_reframer_with_config_example.txt"
    )
    config_mapping_example = load_txt_file(
        "examples/example_fox/input/config_mapping_example.txt"
    )
    query_reframer_with_metatdata_examples = load_txt_file(
        "examples/example_fox/input/query_reframer_examples.txt"
    )
    config = load_json_file("examples/example_fox/input/config_mapping_fox.json")
    metadata = load_txt_file("examples/example_fox/input/meta_information_fox.txt")

    query_reframer_instance = QueryReframer(
        config_mapping_prompt=config_mapping_prompt,
        query_reframer_with_config_prompt=query_reframer_with_config_prompt,
        query_reframer_with_metadata_prompt=query_reframer_with_metadata_prompt,
        query_reframer_with_config_examples=query_reframer_with_config_examples,
        config_mapping_example=config_mapping_example,
        query_reframer_with_metatdata_examples=query_reframer_with_metatdata_examples,
        config=config,
        metadata_file_path="examples/example_fox/input/tables_metadata.json",
    )

    intent_prompt = load_txt_file("examples/example_fox/input/intent_engine_prompt.txt")
    intent_examples = load_txt_file(
        "examples/example_fox/input/intent_engine_example.txt"
    )
    intent_engine_instance = IntentEngine(
        system_prompt=intent_prompt,
        examples=intent_examples,
        metadata=metadata,
    )

    query_builder_instance = QueryBuilder(schema_name="GOLD_PERFORMANCE_AND_RATINGS")
    query_validator_instance = QueryValidator()
    query_executor_instance = QueryExecutor()
    intent_ambiguity_instance = IntentAmbiguityHandler(
        ambiguous_fields_file="data/input/ambigious_fields.json"
    )

    # Initialize the graph
    graph = FoxFramework(
        config_file_path="notebooks/config.yaml",
        table_selector_instance=table_selector_instance,
        query_reframer_instance=query_reframer_instance,
        intent_engine_instance=intent_engine_instance,
        query_builder_instance=query_builder_instance,
        query_validator_instance=query_validator_instance,
        query_executor_instance=query_executor_instance,
        intent_ambiguity_instance=intent_ambiguity_instance,
        interrupt_before=interrupt_before,
    )
    state = FoxState()
    # example: What is the average audience rating for cable networks on 2025-03-30?
    query = input("Enter user query:")
    state["query"] = query

    state["model_type"] = "openai"
    state["model_name"] = "gpt-4.1"
    state["temperature"] = "0.1"

    thread_id = str(uuid.uuid4())
    state["thread_id"] = thread_id

    # Initial run
    response = graph.run(
        thread_id=thread_id,
        state=state,
        model_name="openai",
        model_type="gpt-4.1",
        temperature=0.1,
    )

    # snapshot values
    state = response.values
    state_id = response.values.get("state_id") if hasattr(response, "values") else None
    while True:
        current_state_id = state.get("state_id")
        logger.info(f"Current state_id: {current_state_id}")

        if current_state_id in [1, 9, -1]:
            logger.info(" Terminating conversation.")
            print(state.get("selected_tables"))
            break

    # while True:
    #     logger.info(thread_id)
    #     state_id = (
    #         response.values.get("state_id") if hasattr(response, "values") else None
    #     )
    #     if state_id == 4:  # Intent ambiguity
    #         user_message = response.values.get("user_message", "")
    #         user_query = input(f"{user_message} \nPlease enter your clarified query: ")

    #         # Re-run the graph
    #         response = graph.run(
    #             thread_id=thread_id, state=state, updated_state={"query": user_query}
    #         )
    #         state = response.values
    #         print(state)
    #         # break

    #     elif state_id == 9:  # User followup query
    #         followup_yn = input(
    #             "Do you want to ask followup query? If yes, respond with 'y': "
    #         )
    #         if followup_yn.lower() == "y":
    #             followup_query = input("Ask followup query: ")
    #             response = graph.run(
    #                 thread_id=thread_id,
    #                 state=state,
    #                 updated_state={"query": followup_query},
    #             )
    #             logger.info("Graph response after Followup query:", response)
    #         else:
    #             logger.info("User does not want to ask followup query.")
    #             break
    logger.info("Conversation completed.")
