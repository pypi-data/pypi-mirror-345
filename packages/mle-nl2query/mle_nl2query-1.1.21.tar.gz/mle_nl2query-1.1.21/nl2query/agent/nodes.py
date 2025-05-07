from loguru import logger

from nl2query.core.decorators import handle_exceptions


class StartNode:
    def __init__(self, config):
        self._config = config

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at initial node.")
            state["state_id"] = 0
            state["conversation_messages"] = []
            state["errors"] = []
            state["query"] = state["query"]
            if not state["query"]:
                raise Exception("Error at StartNode: 'query'")

            state["user_message"] = []
            state["raw_messages"] = []
            state["messages"] = []
            state["intent_ambiguity"] = {"ambiguous_fields": {}}
            state["intent_filters"] = {"filterable_fields": {}}
            state["regenerate_intent_yn"] = False
            state.update(self._config)
            return state
        except Exception as e:
            raise Exception(f"Error at StartNode: {e}")


class TableSelectorNode:
    def __init__(self, table_selector):
        self._table_selector = table_selector

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at tables selector node.")
            state["state_id"] = 1
            _, response = self._table_selector.run(state)
            state["selected_tables"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at TableSelectorNode: {e}")


class QueryReframerNode:
    def __init__(self, query_reframer):
        self._query_reframer = query_reframer

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at query reframer node.")
            state["state_id"] = 2
            _, response = self._query_reframer.run(state)
            state["reframed_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryReframerNode: {e}")


class IntentEngineNode:
    def __init__(self, intent_engine):
        self._intent_engine = intent_engine

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at intent engine node.")
            state["state_id"] = 3
            _, response = self._intent_engine.run(state)
            state["intent_json"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at IntentEngineNode: {e}")


class IntentAmbiguityCheckerNode:
    def __init__(self, intent_ambiguity):
        self._intent_ambiguity = intent_ambiguity

    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at intent ambiguity checker node.")
            state["state_id"] = 4
            state = self._intent_ambiguity.process_ambiguity(state)
            return state
        except Exception as e:
            raise Exception(f"Error at IntentAmbiguityHandlerNode: {e}")


class IntentAmbiguityHandlerNode:
    def __init__(self, intent_ambiguity):
        self._intent_ambiguity = intent_ambiguity

    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at intent ambiguity handler.")
            state["state_id"] = 5
            state = self._intent_ambiguity.handle_ambiguity(state)
            # logger.info(response)
            return state
        except Exception as e:
            raise Exception(f"Error at IntentAmbiguityHandlerNode: {e}")


class IntentFilterCheckerNode:
    def __init__(self, intent_filter):
        self._intent_filter = intent_filter

    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at intent filter handler.")
            state["state_id"] = 6
            return state
        except Exception as e:
            raise Exception(f"Error at IntentFilterCheckerNode: {e}")


class QueryBuilderNode:
    def __init__(self, query_builder):
        self._query_builder = query_builder

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at query builder node.")
            state["state_id"] = 7
            state, response = self._query_builder.run(state)
            state["initial_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryBuilderNode: {e}")


class QueryCorrectorNode:
    def __init__(self, query_corrector):
        self._query_corrector = query_corrector

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at query corrector node.")
            state["state_id"] = 8
            _, response = self._query_corrector.run(state)
            state["validated_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryCorrectorNode: {e}")


class QueryExecutorNode:
    def __init__(self, query_executor):
        self._query_executor = query_executor

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at query executor node.")
            state["state_id"] = 9
            _, response = self._query_executor.run(state)
            state["output_response"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryExecutorNode: {e}")


class UserFollowUpNode:
    def __init__(self):
        pass  # TODO add here

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            # logger.info("I am here at User followup node.")
            state["state_id"] = 10
            state["intent_ambiguity"] = {"ambiguous_fields": {}}
            state["intent_filters"] = {"filterable_fields": {}}
            state["proceed_to_query_builder_yn"] = False
            return state
        except Exception as e:
            raise Exception(f"Error at UserFollowUpNode: {e}")


class LastNode:
    def __init__(self):
        pass  # TODO add here

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            logger.info("I am here at last node.")
            state["state_id"] = -1
            return state
        except Exception as e:
            raise Exception(f"Error at LastNode: {e}")
