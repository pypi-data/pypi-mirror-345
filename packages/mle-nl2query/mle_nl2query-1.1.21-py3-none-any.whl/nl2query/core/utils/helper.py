import msgpack
from langgraph.checkpoint.memory import MemorySaver


class CustomMemorySaver(MemorySaver):
    def serialize(self, state):
        # Remove non-serializable objects before serialization.
        for key in [
            "table_selector_instance",
            "query_reframer_instance",
            "intent_engine_instance",
            "query_builder_instance",
            "query_validator_instance",
            "query_executor_instance",
        ]:
            state.pop(key, None)  # Remove key if it exists.
        try:
            return msgpack.packb(state)
        except Exception as e:
            raise Exception(f"Error during state serialization: {e}")
