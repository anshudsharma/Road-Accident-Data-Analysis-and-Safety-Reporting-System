import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


if __name__ == "__main__":
    conn = get_connection()
    if conn.is_connected():
        print("Connected successfully to the Python matrix, sir! 🚀")
    conn.close()
