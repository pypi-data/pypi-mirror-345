import yaml
import uuid
from loguru import logger
from typing import Any, Optional, Dict, Set, Tuple
from IPython.display import Image, display
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from nl2query.core.logger import init_logging
from nl2query.agent.state import State
from nl2query.agent.nodes import (
    StartNode,
    TableSelectorNode,
    QueryReframerNode,
    IntentEngineNode,
    QueryBuilderNode,
    QueryCorrectorNode,
    QueryExecutorNode,
    IntentAmbiguityHandlerNode,
    IntentAmbiguityCheckerNode,
    IntentFilterCheckerNode,
    LastNode,
    UserFollowUpNode,
)
from nl2query.agent.node_selector import (
    select_next_node_after_tables_selector,
    select_next_node_after_query_reframer,
    select_next_node_after_intent_engine,
    select_next_node_after_intent_ambiguity_checker_engine,
    select_next_node_after_intent_filter_checker,
    select_next_node_after_query_builder,
    select_next_node_after_query_corrector,
    select_next_node_after_query_executor,
    select_next_node_after_followup_query,
)


class NL2QueryGraph:
    def __init__(
        self,
        config_file_path: str = "config.yaml",
        table_selector_instance=None,
        query_reframer_instance=None,
        intent_engine_instance=None,
        query_builder_instance=None,
        query_validator_instance=None,
        query_executor_instance=None,
        intent_ambiguity_instance=None,
        intent_filter_checker=None,
        interrupt_before=None,
        log_file_name: str = "logs",
    ):
        with open(config_file_path, "r") as file:
            self.config = yaml.safe_load(file)
        logger.info(f"Config loaded: {self.config}")

        self.query_reframer = query_reframer_instance
        self.table_selector = table_selector_instance
        self.intent_engine = intent_engine_instance
        self.query_builder = query_builder_instance
        self.query_validator = query_validator_instance
        self.query_executor = query_executor_instance
        self.intent_ambiguity_handler = intent_ambiguity_instance
        self.intent_filter_checker = intent_filter_checker
        self.interrupt_before = interrupt_before

        self.graph = StateGraph(State)
        self.memory = MemorySaver()
        self.initial_state = State()
        self.edges: Set[Tuple[str, str]] = set()
        self.conditional_edges: Dict[str, Dict[str, Any]] = {}

        self._setup_nodes()
        self._setup_edges()
        self._apply_edges()
        self.compiled_graph = self.compile()
        init_logging(filename=log_file_name)

    def _setup_nodes(self):
        self.graph.add_node("start_node", StartNode(config=self.config))
        logger.info("Added node: start_node")
        if self.config.get("tables_selector_yn", False):
            self.graph.add_node(
                "tables_selector_node",
                TableSelectorNode(table_selector=self.table_selector),
            )
            logger.info("Added node: tables_selector_node")
        if self.config.get("query_reframer_yn", False):
            self.graph.add_node(
                "query_reframer_node",
                QueryReframerNode(query_reframer=self.query_reframer),
            )
            logger.info("Added node: query_reframer_node")
        if self.config.get("intent_yn", False):
            self.graph.add_node(
                "intent_engine_node", IntentEngineNode(intent_engine=self.intent_engine)
            )
            logger.info("Added node: intent_engine_node")
        if self.config.get("intent_ambiguity_yn", False):
            self.graph.add_node(
                "intent_ambiguity_checker_node",
                IntentAmbiguityCheckerNode(
                    intent_ambiguity=self.intent_ambiguity_handler
                ),
            )
            logger.info("Added node: intent_ambiguity_checker_node")
        if self.config.get("intent_ambiguity_yn", False):
            self.graph.add_node(
                "intent_ambiguity_handler_node",
                IntentAmbiguityHandlerNode(
                    intent_ambiguity=self.intent_ambiguity_handler
                ),
            )
            logger.info("Added node: intent_ambiguity_handler_node")
        if self.config.get("intent_filterable_yn", False):
            self.graph.add_node(
                "intent_filter_checker_node",
                IntentFilterCheckerNode(intent_filter=self.intent_filter_checker),
            )
            logger.info("Added node: intent_filter_checker_node")
        if self.config.get("query_builder_yn", False):
            self.graph.add_node(
                "query_builder_node", QueryBuilderNode(query_builder=self.query_builder)
            )
            logger.info("Added node: query_builder_node")
        if self.config.get("query_correcter_yn", False):
            self.graph.add_node(
                "query_corrector_node",
                QueryCorrectorNode(query_corrector=self.query_validator),
            )
            logger.info("Added node: query_corrector_node")
        if self.config.get("query_executor_yn", False):
            self.graph.add_node(
                "query_executor_node",
                QueryExecutorNode(query_executor=self.query_executor),
            )
            logger.info("Added node: query_executor_node")
        self.graph.add_node("user_followup_query_node", UserFollowUpNode())
        self.graph.add_node("last_node", LastNode())
        logger.info("Added node: last_node")

    def _get_default_edge_mapping(self) -> Dict[str, Dict[str, Any]]:
        return {
            "start_node": {
                "condition": lambda state: "tables_selector_node"
                if state.get("tables_selector_yn", False)
                else "query_reframer_node",
                "targets": {"tables_selector_node", "query_reframer_node"},
            },
            "tables_selector_node": {
                "condition": select_next_node_after_tables_selector,
                "targets": {"query_reframer_node", "intent_engine_node", "last_node"},
            },
            "query_reframer_node": {
                "condition": select_next_node_after_query_reframer,
                "targets": {"intent_engine_node", "query_builder_node", "last_node"},
            },
            "intent_engine_node": {
                "condition": select_next_node_after_intent_engine,
                "targets": {
                    "intent_ambiguity_checker_node",
                    "intent_filter_checker_node",
                    "query_builder_node",
                    "last_node",
                },
            },
            "intent_ambiguity_checker_node": {
                "condition": select_next_node_after_intent_ambiguity_checker_engine,
                "targets": {
                    "intent_ambiguity_handler_node",
                    "query_builder_node",
                    "intent_engine_node",
                    "intent_filter_checker_node",
                    "last_node",
                },
            },
            "intent_filter_checker_node": {
                "condition": select_next_node_after_intent_filter_checker,
                "targets": {"query_builder_node", "intent_engine_node", "last_node"},
            },
            "query_builder_node": {
                "condition": select_next_node_after_query_builder,
                "targets": {"query_corrector_node", "last_node"},
            },
            "query_corrector_node": {
                "condition": select_next_node_after_query_corrector,
                "targets": {
                    "user_followup_query_node",
                    "query_executor_node",
                    "last_node",
                },
            },
            "query_executor_node": {
                "condition": select_next_node_after_query_executor,
                "targets": {
                    "table_selector_node",
                    "user_followup_query_node",
                    "last_node",
                },
            },
            "user_followup_query_node": {
                "condition": select_next_node_after_followup_query,
                "targets": {
                    "tables_selector_node",
                    "query_reframer_node",
                    "intent_engine_node",
                    "query_builder_node",
                    "last_node",
                },
            },
        }

    def _setup_edges(self):
        self.edges.add((START, "start_node"))
        logger.info("Added edge to edges set: START -> start_node")
        self.conditional_edges.update(self._get_default_edge_mapping())
        self.edges.add(
            ("intent_ambiguity_handler_node", "intent_ambiguity_checker_node")
        )
        self.edges.add(("intent_filter_handler_node", "intent_filter_checker_node"))

        self.edges.add(("last_node", END))

    def _apply_edges(self):
        for from_node, to_node in self.edges:
            if from_node in self.graph.nodes or from_node == START:
                if to_node in self.graph.nodes or to_node == END:
                    self.graph.add_edge(from_node, to_node)
                    logger.info(f"Applied edge: {from_node} -> {to_node}")
                else:
                    logger.warning(
                        f"Skipping edge {from_node} -> {to_node}: Target node missing"
                    )
            else:
                logger.warning(
                    f"Skipping edge {from_node} -> {to_node}: Source node missing"
                )

        # Apply conditional edges
        for source, config_data in self.conditional_edges.items():
            if source in self.graph.nodes:
                valid_targets = config_data["targets"] & set(self.graph.nodes.keys())
                if valid_targets:
                    self.graph.add_conditional_edges(
                        source, config_data["condition"], list(valid_targets)
                    )
                    logger.info(
                        f"Applied conditional edges from {source} to {valid_targets}"
                    )
                else:
                    self.graph.add_edge(source, "last_node")
                    logger.info(
                        f"No valid targets for {source}, applied edge to last_node"
                    )
            else:
                logger.warning(f"Source node {source} not in graph, skipping")

    def remove_edge(self, from_node: str, to_node: str):
        edge = (from_node, to_node)
        if edge in self.edges:
            self.edges.remove(edge)
            logger.info(f"Removed edge: {from_node} -> {to_node}")
        elif (
            from_node in self.conditional_edges
            and to_node in self.conditional_edges[from_node]["targets"]
        ):
            self.conditional_edges[from_node]["targets"].remove(to_node)
            logger.info(f"Removed conditional target {to_node} from {from_node}")

    def add_edge(self, from_node: str, to_node: str):
        if (from_node in self.graph.nodes or from_node == START) and (
            to_node in self.graph.nodes or to_node == END
        ):
            self.edges.add((from_node, to_node))
            logger.info(f"Added edge: {from_node} -> {to_node}")
        else:
            logger.warning(
                f"Cannot add edge {from_node} -> {to_node}: One or both nodes not in graph"
            )

    def add_conditional_edge(
        self, from_node: str, condition: callable, targets: Set[str]
    ):
        if from_node in self.graph.nodes:
            self.conditional_edges[from_node] = {
                "condition": condition,
                "targets": targets,
            }
            logger.info(
                f"Added conditional edge for {from_node} with targets {targets}"
            )
        else:
            logger.warning(
                f"Cannot add conditional edge for {from_node}: Node not in graph"
            )

    def compile(self) -> Any:
        return self.graph.compile(
            checkpointer=self.memory, interrupt_before=self.interrupt_before
        )

    def visualize(self):
        compiled_graph = self.compile()
        display(Image(compiled_graph.get_graph().draw_mermaid_png()))

    def list_added_nodes(self):
        logger.info("Listing all nodes in the graph:")
        for node in self.compiled_graph.nodes:
            logger.info(f"Node: {node}")
        return list(self.graph.nodes)

    # TODO run(thread_id, {user_query, followup_query})
    def run(
        self,
        thread_id=None,
        state: Optional[State] = None,
        updated_state=None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Executes the graph internally until completion.
        Extra kwargs (query, model_name, etc.) can be injected into the state if needed.
        Returns the final result instead of a generator.
        """
        thread_id = thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 2000}
        response_type = state.get("response_type", "regular") if state else "regular"

        if response_type == "streaming":
            logger.info("Running in streaming mode with feedback loop...")
            input_state = state
            final_response = []
            # while True:
            iterator = self.compiled_graph.stream(
                input_state, config=config, stream_mode="values"
            )
            for event in iterator:
                final_response.append(str(event))
            input_state = None
            current_state = self.compiled_graph.get_state(config)
            return current_state

        elif response_type == "regular":
            input_state = state
            if updated_state:
                self.compiled_graph.invoke(
                    Command(update=updated_state, resume="Lets go"), config=config
                )
            else:
                self.compiled_graph.invoke(input_state, config=config)

            input_state = None
            current_state = self.compiled_graph.get_state(config)

            return current_state
        else:
            raise ValueError(f"Unknown response_type: {response_type}")
