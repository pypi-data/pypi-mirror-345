from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import snowflake.connector

from nl2query import settings


@contextmanager
def get_db():
    """Context manager for getting a database session."""
    # Set up the database engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_sql_query(query):
    """Executes a raw SQL query on the PostgreSQL database using a session from get_db."""
    try:
        # Use the context manager to manage the session
        with get_db() as db:
            result = db.execute(text(query))  # Execute query using session
            if query.strip().upper().startswith("SELECT"):
                return result.fetchall()
            else:
                print("Query executed successfully!")
                return None
    except SQLAlchemyError as e:
        print(f"Error executing query: {e}")


def create_snowflake_connection():
    conn = snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
    )
    return conn


def execute_snowflake_query(query):
    conn = create_snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()

        return results
    except Exception as e:
        print("Error executing query:", e)
        raise e

    finally:
        cur.close()
        conn.close()
