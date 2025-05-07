import json
from loguru import logger

from nl2query.core.path_setup import input_dir
from nl2query.core.base_module import BaseModule


class IntentAmbiguityHandler(BaseModule):
    """
    A class to handle ambiguity in intent fields.
    The run() method processes ambiguity (if any) and, if the user has provided input,
    it handles that input to update how the query is reframed.
    """

    def __init__(
        self,
        system_prompt: str = None,
        examples: str = None,
        ambiguous_fields_file: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(system_prompt, examples, *args, **kwargs)
        if ambiguous_fields_file is None:
            ambiguous_fields_file = f"{input_dir}/ambigious_fields.json"
        with open(ambiguous_fields_file, "r") as f:
            self.ambiguous_data = json.load(f)

    def process_ambiguity(self, state: dict) -> dict:
        """
        Checks if the intent in state contains any ambiguous fields.
        If found, marks them as unresolved, picks the first for processing,
        and generates a clarification message which is set in state["user_message"].
        Otherwise, it marks ambiguity as not existing.
        """
        ambiguous_data_mapping = self.ambiguous_data.get("mapping", {})
        intent_ambiguity_data = state.get("intent_ambiguity")

        if "exists" not in intent_ambiguity_data:
            ambiguity_check = False
            intent_entities = [
                field
                for entity in state["intent_json"].get("entities", [])
                for field in entity.get("fields")
            ]

            for entity in intent_entities:
                if entity in ambiguous_data_mapping:
                    ambiguity_check = True
                    intent_ambiguity_data["exists"] = True
                    intent_ambiguity_data["ambiguous_fields"][
                        ambiguous_data_mapping[entity]
                    ] = "unresolved"

            if ambiguity_check:
                intent_ambiguity_data["is_processing"] = list(
                    intent_ambiguity_data["ambiguous_fields"].keys()
                )[0]
                user_message = self.generate_ambiguity_message(
                    intent_ambiguity_data["is_processing"]
                )
                state["user_message"] = user_message

            else:
                intent_ambiguity_data["exists"] = False

        else:
            if intent_ambiguity_data["exists"]:
                user_message = self.generate_ambiguity_message(
                    intent_ambiguity_data["is_processing"]
                )
                state["user_message"] = user_message

        if not intent_ambiguity_data["exists"] and not state["intent_filterable_yn"]:
            state["proceed_to_query_builder_yn"] = True

        state["intent_ambiguity"] = intent_ambiguity_data

        logger.info(f"Intent ambiguity data: {intent_ambiguity_data}")
        return state

    def generate_ambiguity_message(self, field: str) -> str:
        """
        Generates a clarification message by listing all possible options
        for the given ambiguity category from the ambiguous_fields.json.
        """
        messages = ["Did you mean:"]
        for desc in self.ambiguous_data.get("mapping_description", {}).get(field, []):
            messages.append(f"{desc.get('idx')}. {desc.get('value')}")
        return "\n".join(messages)

    def handle_ambiguity(self, state: dict) -> dict:
        """
        Processes the user’s response (stored in state["query"]) for disambiguation.
        It updates the state's reframed query with clarification details and marks the ambiguous field as resolved.
        If additional ambiguous fields remain unresolved, it updates state["user_message"] accordingly.
        """
        user_input = state.get("query", "").strip().lower()
        ambiguous_data_description = self.ambiguous_data.get("mapping_description", {})
        intent_ambiguity_data = state.get("intent_ambiguity", {})
        processing_field = intent_ambiguity_data.get("is_processing")

        # List available option indices for the current ambiguous field.
        available_options = [
            str(desc.get("idx"))
            for desc in ambiguous_data_description.get(processing_field, [])
        ]

        if user_input in available_options:
            for desc in ambiguous_data_description.get(processing_field, []):
                if str(desc.get("idx")) == user_input:
                    message = f"\nWe are interpreting the field as `{desc.get('field')}` ({desc.get('info')}).\n"
                    state["reframed_query"] = state.get("reframed_query", "") + message
                    state["regenerate_intent_yn"] = True

            logger.info(
                f"Reframed query after handling ambiguity: {state['reframed_query']}"
            )
            # Mark the current ambiguous field as resolved, only if the user_input is in available_options
            if processing_field in intent_ambiguity_data.get("ambiguous_fields", {}):
                intent_ambiguity_data["ambiguous_fields"][processing_field] = "resolved"

        # If user_input is not in available options, do not mark processing_field as resolved.

        ambiguous_fields = intent_ambiguity_data.get("ambiguous_fields", {})

        if isinstance(ambiguous_fields, dict):
            unresolved_fields = [
                field
                for field, status in ambiguous_fields.items()
                if status == "unresolved"
            ]
        else:
            logger.warning(
                f"Expected a dictionary for ambiguous_fields, but got: {type(ambiguous_fields)}"
            )
            unresolved_fields = []

        if unresolved_fields:
            intent_ambiguity_data["is_processing"] = unresolved_fields[0]
            state["user_message"] = self.generate_ambiguity_message(
                unresolved_fields[0]
            )
        else:
            intent_ambiguity_data["exists"] = False

        state["intent_ambiguity"] = intent_ambiguity_data

        logger.info(f"After handling intent ambiguity: {intent_ambiguity_data}")
        return state

    def run(self, state: dict) -> dict:
        pass
