import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from a .env file
load_dotenv()

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    Returns:
        connection (MySQLConnection): A connection object if successful, None otherwise.
    """
    try:
        # Ensure required environment variables are set
        required_env_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
        for var in required_env_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"Environment variable '{var}' is not set")

        # Create a connection
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            logger.info(f"Connected to MySQL database '{os.getenv('DB_NAME')}'")
        return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None
    except EnvironmentError as env_error:
        logger.error(env_error)
        return None


def close_db_connection(connection):
    """
    Close the database connection.
    Args:
        connection (MySQLConnection): The connection object to close.
    """
    if connection and connection.is_connected():
        connection.close()
        logger.info("MySQL connection is closed")
