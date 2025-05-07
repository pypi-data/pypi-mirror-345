import operator

from typing_extensions import TypedDict
from typing import Annotated, Literal, Dict


class BaseState(TypedDict):
    state_id: int
    thread_id: str
    version: str
    response_type: Literal["streaming", "regular"]
    errors: Annotated[list, operator.add]
    query: str
    model_type: str
    model_name: str
    temperature: str
    results: str
    user_message: str
    raw_messages: list
    messages: list


class State(BaseState, total=False):
    tables_selector_yn: bool
    follow_up_query_yn: bool
    query_reframer_yn: bool
    query_reframer_metadata_yn: bool
    query_reframer_examples_yn: bool
    query_reframer_config_yn: bool
    query_reframer_rag_yn: bool
    refarmed_query: str
    reframed_query_with_metadata: str
    reframed_query_with_config: str
    selected_tables: list
    intent_yn: bool
    rag_yn: bool
    config_mapping: Dict
    query_builder_yn: bool
    intent_ambiguity_yn: bool
    intent_filterable_yn: bool
    query_correcter_yn: bool
    query_executor_yn: bool
    reframed_query: str
    initial_query: str
    validated_query: str
    intent_json: Dict
    intent_ambiguity: list
    regenerate_intent_yn: bool
    metadata: Dict
    proceed_to_query_builder_yn: bool
    table_selector_response_time: float
    query_validator_response_time: float
    query_reframer_response_time: float
    query_builder_processing_time: float
    intent_engine_processing_time: float
    query_executor_response_time: float
    query_executor_error: str
    mapping_output: Dict
    selected_table_reason: str
    db_type: Literal["postgres", "snowflake"]
    output_response: str  # output from db
