import singlestoredb as s2
from contextlib import contextmanager
from app.core.config import DATABASE_CONFIG

@contextmanager
def get_db_connection():
    connection = None
    try:
        connection = s2.connect(**DATABASE_CONFIG)
        yield connection
    except Exception as e:
        print(f"Database connection error: {e}") # Or use proper logging
        raise
    finally:
        if connection:
            connection.close()

# Example of how to use it:
# with get_db_connection() as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("SELECT 1")
#         result = cursor.fetchone()
#         print(result) 