import psycopg2
from psycopg2 import sql
import os
DB_NAME = "WSCBS_assignment"

# SYSTEM_DB_CONFIG = {
#     "dbname": "postgres",
#     "user": "postgres",
#     "password": "123456",
#     "host": "localhost",
#     "port": 5432
# }

# DB_CONFIG = {
#     "dbname": DB_NAME,
#     "user": "postgres",
#     "password": "123456",
#     "host": "localhost",
#     "port": 5432
# }

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@db-services:5432/WSCBS_assignment")

def connect_db():
    try:
        # connection = psycopg2.connect(**DB_CONFIG)
        connection = psycopg2.connect(DATABASE_URL)
        print("Database connected successfully!")
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {type(e)}, {e}")
        exit()


# Connect to the system database and create a new database if it doesn't exist
def create_db():
    try:
        # connection = psycopg2.connect(**SYSTEM_DB_CONFIG)
        connection = psycopg2.connect(DATABASE_URL)
        connection.autocommit = True  # Enable autocommit for CREATE DATABASE
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
            cursor.execute(
                """
                CREATE SCHEMA IF NOT EXISTS auth;
                
                DROP TABLE IF EXISTS auth.users CASCADE;
                
                CREATE TABLE IF NOT EXISTS auth.users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                );
                """
            )
            connection.commit()
            print("Schemas and tables created successfully!")
    except Exception as e:
        print(f"Failed to create schemas or tables: {e}")
        connection.rollback()


def add_user(connection, username, password_hash, email=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auth.users (username, password_hash, email)
                VALUES (%s, %s, %s) RETURNING id;
                """,
                (username, password_hash, email)
            )
            result = cursor.fetchone()
            connection.commit()
            print(f"User '{username}' added successfully.")
            return result
    except Exception as e:
        print(f"Failed to add user: {e}")
        connection.rollback()


def get_user(connection, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, created_at FROM auth.users WHERE username = %s;
                """,
                (username,)
            )
            user = cursor.fetchone()
            if user:
                print(f"User found: {user}")
            else:
                print(f"User '{username}' not found.")
            return user
    except Exception as e:
        print(f"Failed to fetch user: {e}")


def get_password(connection, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT password_hash FROM auth.users WHERE username = %s;
                """,
                (username,)
            )
            password = cursor.fetchone()
            return password
    except Exception as e:
        print(f"Failed to fetch password: {e}")


# Update user's email or password (Update)
def update_user(connection, username, new_password_hash=None, new_email=None):
    try:
        with connection.cursor() as cursor:
            if new_password_hash:
                cursor.execute(
                    """
                    UPDATE auth.users
                    SET password_hash = %s
                    WHERE username = %s
                    """,
                    (new_password_hash, username)
                )
            if new_email:
                cursor.execute(
                    """
                    UPDATE auth.users
                    SET email = %s
                    WHERE username = %s
                    """,
                    (new_email, username)
                )
            connection.commit()
            print(f"User '{username}' updated successfully.")
    except Exception as e:
        print(f"Failed to update user: {e}")
        connection.rollback()


# Delete a user by username (Delete)
def delete_user(connection, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM auth.users WHERE username = %s;
                """,
                (username,)
            )
            connection.commit()
            print(f"User '{username}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete user: {e}")
        connection.rollback()


if __name__ == "__main__":
    create_db()
    setup_db(connection=connect_db())
