import time
from loguru import logger
from nl2query.db.db_connector import execute_sql_query, execute_snowflake_query


class QueryExecutor:
    def run(self, state):
        """Main function to execute the query executor."""
        start_time = time.time()
        try:
            if state["db_type"] == "postgres":
                query = state["validated_query"]
                result = execute_sql_query(query)
                state["output_response"] = result
            elif state["db_type"] == "snowflake":
                query = state["validated_query"]
                result = execute_snowflake_query(query)
                state["output_response"] = result
            else:
                raise ValueError("Unsupported db_type specified in the state.")

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            state["query_executor_error"] = str(e)
            result = None

        end_time = time.time()
        response_time = end_time - start_time
        state["query_executor_response_time"] = response_time
        logger.info(f"Query executor response time: {response_time:.4f} seconds")

        if result is not None:
            logger.info(f"Output after executing the generated query: {result}")
        else:
            logger.info(
                "Query execution failed. Check 'query_executor_error' for details."
            )

        return state, result
