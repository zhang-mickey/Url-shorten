import psycopg2
from psycopg2 import sql
import os
DB_NAME = "WSCBS_assignment"

# Initial connection to postgres system database
SYSTEM_DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5432
}

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5432
}

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@db_services:5432/WSCBS_assignment")

def delete_all_urls():
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM url.urls;")
                connection.commit()
                print("All URLs deleted successfully.")
    except Exception as e:
        print(f"Error while deleting URLs: {e}")


def connect_db():
    try:
        # connection = psycopg2.connect(**SYSTEM_DB_CONFIG)
        connection = psycopg2.connect(DATABASE_URL)

        # print("Database connected successfully!")
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {type(e)}, {e}")
        exit()


def create_db():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        # connection = psycopg2.connect(**DB_CONFIG)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
            if cursor.fetchone():
                print(f"Database '{DB_NAME}' already exists.")
            else:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"Database '{DB_NAME}' created successfully.")
        connection.close()
    except Exception as e:
        print(f"Failed to create database: {e}")
        exit()


def setup_db(connection):
    try:
        with connection.cursor() as cursor:
            # DROP TABLE IF EXISTS url.urls CASCADE;
            cursor.execute(
                """
                CREATE SCHEMA IF NOT EXISTS url;
                CREATE TABLE IF NOT EXISTS url.urls (
                    short_id CHAR(12) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    original_url VARCHAR(2048) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    expired_at TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_id ON url.urls (user_id);
                """
            )
            connection.commit()
            print("Schemas and tables created successfully!")
            delete_all_urls()
    except Exception as e:
        print(f"Failed to create schemas or tables: {e}")
        connection.rollback()


# Add a new URL mapping (Create)
def add_url_mapping(connection, short_id, user_id, original_url, expired_at=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO url.urls (short_id, user_id, original_url, expired_at)
                VALUES (%s, %s, %s, %s)
                """,
                (short_id, user_id, original_url, expired_at)
            )
            connection.commit()
            print(f"URL mapping with short_id '{short_id}' added successfully.")
    except Exception as e:
        print(f"Failed to add URL mapping: {e}")
        connection.rollback()


def get_by_short_id(connection, short_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT original_url, expired_at, user_id FROM url.urls WHERE short_id = %s;
                """,
                (short_id,)
            )

            result = cursor.fetchone()
            if result:
                return {"user_id": result[2], "original_url": result[0], "expired_at": result[1]}
            return result
            # if not result:
            #     original_url, expired_at, user_id = result
            #     print(f"Original URL: {original_url}, Expired At: {expired_at}")
            # else:
            #     print(f"No URL found for short_id '{short_id}'.")
    except Exception as e:
        print(f"Failed to fetch URL mapping: {e}")


def get_all(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT short_id, original_url, expired_at,user_id FROM url.urls;")
            urls = cursor.fetchall()
            if not urls:
                return []
            else:
                urls = [{"value": row[0], "original_url": row[1], "expiry_time": row[2], "user_id": row[3]} for row in
                        urls]
                return urls
    except Exception as e:
        print(f"Failed to fetch URL mapping: {e}")


# Update a URL mapping (Update)
def update_url_mapping(connection, short_id, new_original_url=None, new_expired_at=None):
    try:
        with connection.cursor() as cursor:
            if new_original_url:
                cursor.execute(
                    """
                    UPDATE url.urls
                    SET original_url = %s
                    WHERE short_id = %s
                    """,
                    (new_original_url, short_id)
                )

            if new_expired_at:
                cursor.execute(
                    """
                    UPDATE url.urls
                    SET expired_at = %s
                    WHERE short_id = %s
                    """,
                    (new_expired_at, short_id)
                )
            connection.commit()
            print(f"URL mapping with short_id '{short_id}' updated successfully.")
    except Exception as e:
        print(f"Failed to update URL mapping: {e}")
        print(f"short_id '{short_id}', new_expired_at '{new_expired_at}', new_original_url '{new_original_url}'")
        connection.rollback()


# Delete a URL mapping by short_id (Delete)
def delete_url_mapping(connection, short_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM url.urls WHERE short_id = %s RETURNING short_id
                """,
                (short_id,)
            )
            result = cursor.fetchone()
            connection.commit()
            print(f"URL mapping with short_id '{short_id}' deleted successfully.")
            return result
    except Exception as e:
        print(f"Failed to delete URL mapping: {e}")
        connection.rollback()


def delete_expired_urls(connection):
    """Delete expired URLs from the database."""
    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM url.urls WHERE expired_at IS NOT NULL AND expired_at < NOW()")
            connection.commit()
            # print("Deleted expired URLs")
    except Exception as e:
        print(f"Error deleting expired URLs: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_db()
    setup_db(connection=connect_db())
