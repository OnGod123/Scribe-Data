import os
import psycopg2

def create_table():
    """Creates a PostgreSQL table for storing translations."""
    conn = None
    cur = None
    try:
        # Connect to the translation database using environment variables
        conn = psycopg2.connect(
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        print("Connected to the database.")

        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS translations (
            id SERIAL PRIMARY KEY,
            source_lang VARCHAR(2) NOT NULL,
            phrase TEXT NOT NULL,
            french TEXT,
            spanish TEXT,
            portuguese TEXT,
            german TEXT
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'translations' created successfully.")

    except psycopg2.Error as error:
        print("Database error occurred:", error)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_table()
