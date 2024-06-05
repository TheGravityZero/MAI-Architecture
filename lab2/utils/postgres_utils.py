import os
import psycopg2

from dotenv import load_dotenv
load_dotenv()

class PostgresDB:
    def __init__(self, db_name = 'postgres') -> None:
        self.db_name = db_name
        self.user = os.environ.get("POSTGRES_USER_NAME", "postgres")
        self.password = os.environ.get("POSTGRES_USER_PASSWORD", "postgres")
        self.host = os.environ.get("POSTGRES_HOST", "postgres")
        self.port = os.environ.get("POSTGRES_PORT", "5432")
        self.conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        

    def get_cursor(self) -> psycopg2.extensions.cursor:
        self.cur = self.conn.cursor()
        return self.cur

    def close_connection(self):
        self.cur.close()
        if self.conn:
            self.conn.close()


def init_postgres():
    connection = PostgresDB()
    cursor = connection.get_cursor()
    cursor.connection.autocommit = True
    cmd = f"SELECT datname FROM pg_database WHERE datname = 'users_db'"
    cursor.execute(cmd)
    data = cursor.fetchall()
    if data:
        print("Postgres has already been created")
        cursor.close()
        return
    
    cmd_drop_db = f"DROP DATABASE IF EXISTS users_db;"
    cmd_create_db = f"CREATE DATABASE users_db;"
    cursor.execute(cmd_drop_db)
    cursor.execute(cmd_create_db)
    cursor.close()
    connection.close_connection()

    connection = PostgresDB("users_db")
    cursor = connection.get_cursor()
    cmd_create_table = """
        CREATE TABLE users 
        (
            id SERIAL,
            login VARCHAR(255),
            name VARCHAR(255),
            surname VARCHAR(255),
            password VARCHAR(255)
        )
    """
    cursor.execute(cmd_create_table)
    cursor.connection.commit()
    connection.close_connection()


if __name__ == '__main__':
    init_postgres()