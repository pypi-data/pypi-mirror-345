from loguru import logger

from nl2query.agent import State


def wrap_state_transition(func):
    def wrapper(state: State):
        if state["state_id"] == -1:
            return "last_node"
        return func(state)

    return wrapper


def handle_exceptions(func):
    def wrapper(self, state: State, **kwargs):
        try:
            return func(self, state, **kwargs)
        except Exception as e:
            logger.info(e)
            state["state_id"] = -1  # Transition to final state
            logger.error(f"An exception occurred: {e}")
            if state.get("errors") is None:
                state["errors"] = []

            # Check if the exception has status_code and detail attributes
            if hasattr(e, "status_code") and hasattr(e, "detail"):
                error_entry = {"status": e.status_code, "detail": str(e.detail)}
            else:
                error_entry = {"status": 500, "detail": str(e)}

            state["errors"].append(error_entry)
            return state

    return wrapper
