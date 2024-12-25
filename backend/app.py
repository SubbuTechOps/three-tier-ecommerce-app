from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
import logging
import os
import sys
import time
from dotenv import load_dotenv

# Configure logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

# Add the parent directory to Python's module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

# Track uptime for health check
start_time = time.time()

def create_app():
    """
    Factory function to create and configure the Flask application.
    Returns:
        The configured Flask app instance.
    """
    app = Flask(__name__)

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Serve static frontend files
    @app.route("/<path:filename>")
    def serve_static(filename):
        """Serve static files like HTML, CSS, or JS from the frontend directory."""
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
        if not os.path.isfile(os.path.join(frontend_path, filename)):
            return jsonify({"message": "File not found"}), 404
        return send_from_directory(frontend_path, filename)

    @app.route("/")
    def serve_index():
        """Serve the default index.html from the frontend directory."""
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
        return send_from_directory(frontend_path, "index.html")

    # Add a health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        uptime = time.time() - start_time
        return jsonify({
            "status": "healthy",
            "uptime": f"{uptime:.2f} seconds"
        }), 200

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(order_bp, url_prefix="/api/orders")

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"message": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"message": "Bad request"}), 400

    return app


if __name__ == "__main__":
    # Create and configure the Flask app
    app = create_app()

    # Determine debug mode from the environment
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    logger.info(f"Starting Flask app in {'debug' if debug_mode else 'production'} mode")

    # Run the app
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
