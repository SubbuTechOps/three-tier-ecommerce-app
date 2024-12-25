from database.db_config import get_db_connection, close_db_connection
import bcrypt  # For password hashing


class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password  # This should store the hashed password

    def to_dict(self):
        """Convert User object to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "username": self.username
        }

    @staticmethod
    def get_user_by_id(user_id):
        """
        Fetch a user by their ID from the database.
        Returns:
            User object if found, else None.
        """
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return None
            return User(user['id'], user['username'], user['password'])
        finally:
            close_db_connection(connection)

    @staticmethod
    def get_user_by_username(username):
        """
        Fetch a user by their username from the database.
        Returns:
            User object if found, else None.
        """
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                return None
            return User(user['id'], user['username'], user['password'])
        finally:
            close_db_connection(connection)

    @staticmethod
    def create_user(username, password):
        """
        Insert a new user into the database with a hashed password.
        Args:
            username (str): The username of the user.
            password (str): The plain-text password to hash and store.
        Returns:
            User: The created User object.
        """
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        try:
            # Hash the password before storing
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            user_id = cursor.lastrowid
            return User(user_id, username, hashed_password)
        except Exception as e:
            connection.rollback()
            raise Exception(f"Error creating user: {e}")
        finally:
            close_db_connection(connection)

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate a user with their username and password.
        Args:
            username (str): The username of the user.
            password (str): The plain-text password to validate.
        Returns:
            User: The authenticated User object if successful, else None.
        """
        user = User.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None
