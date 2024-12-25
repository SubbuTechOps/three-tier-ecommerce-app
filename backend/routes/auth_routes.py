from flask import Blueprint, request, jsonify
from models.user import User

# Initialize Blueprint for Authentication
auth_bp = Blueprint('auth', __name__)

# Signup Route
@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Handle user registration.
    Expects JSON with "username" and "password".
    Returns:
        - 201: User registered successfully.
        - 400: Username or password missing, or username already exists.
        - 500: Internal server error.
    """
    try:
        # Parse JSON payload
        if not request.is_json:
            return jsonify({"message": "Invalid request format. JSON required."}), 400

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate Input
        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        # Check if username already exists
        if User.get_user_by_username(username):
            return jsonify({"message": "Username already exists."}), 400

        # Create new user
        user = User.create_user(username, password)
        return jsonify({"message": "User registered successfully.", "user": user.to_dict()}), 201

    except Exception as e:
        # Log error for debugging
        print(f"Error in signup: {str(e)}")
        return jsonify({"message": "An error occurred during signup.", "error": str(e)}), 500


# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login by verifying credentials.
    Expects JSON with "username" and "password".
    Returns:
        - 200: Login successful with user details.
        - 401: Invalid credentials.
        - 400: Missing required fields.
        - 500: Internal server error.
    """
    try:
        # Parse JSON payload
        if not request.is_json:
            return jsonify({"message": "Invalid request format. JSON required."}), 400

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate Input
        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        # Authenticate user
        user = User.authenticate(username, password)
        if user:
            return jsonify({"message": "Login successful.", "user": user.to_dict()}), 200

        # Invalid credentials
        return jsonify({"message": "Invalid credentials."}), 401

    except Exception as e:
        # Log error for debugging
        print(f"Error in login: {str(e)}")
        return jsonify({"message": "An error occurred during login.", "error": str(e)}), 500
