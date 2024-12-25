from flask import Blueprint, request, jsonify
from database.db_config import get_db_connection, close_db_connection
from models.order import Order

order_bp = Blueprint('orders', __name__)

@order_bp.route('/api/orders', methods=['GET'])
def get_orders():
    """
    Fetch all orders for a specific user.
    Expects a user_id parameter in the query string.
    Returns:
        - 200: A list of orders as JSON.
        - 400: Missing user_id parameter.
    """
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id parameter is required"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch all orders for the user
        cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
        orders = cursor.fetchall()

        # Fetch order items for each order
        for order in orders:
            cursor.execute("""
                SELECT oi.product_id, oi.quantity, p.name, p.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order['id'],))
            items = cursor.fetchall()
            order['items'] = [
                {
                    "product_id": item["product_id"],
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": item["quantity"],
                    "total_price": item["quantity"] * item["price"]
                }
                for item in items
            ]

        return jsonify({"message": "Orders retrieved successfully", "orders": orders}), 200
    finally:
        close_db_connection(connection)

@order_bp.route('/api/orders', methods=['POST'])
def create_order():
    """
    Create a new order for a user.
    Expects JSON with user_id, total_amount, and items (product_id and quantity).
    Returns:
        - 201: Order created successfully.
        - 400: Missing required fields.
    """
    data = request.json
    user_id = data.get('user_id')
    total_amount = data.get('total_amount')
    items = data.get('items')

    if not user_id or not total_amount or not items:
        return jsonify({"message": "user_id, total_amount, and items are required"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        # Insert the new order
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)
        """, (user_id, total_amount))
        order_id = cursor.lastrowid

        # Insert order items
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)  # Default quantity is 1
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, product_id, quantity))

        connection.commit()
        return jsonify({"message": "Order created successfully", "order_id": order_id}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Failed to create order", "error": str(e)}), 500
    finally:
        close_db_connection(connection)

@order_bp.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """
    Fetch a specific order by its ID.
    Args:
        order_id: The ID of the order to fetch.
    Returns:
        - 200: Order details as JSON.
        - 404: Order not found.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch the order
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Fetch the items associated with the order
        cursor.execute("""
            SELECT oi.product_id, oi.quantity, p.name, p.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        order['items'] = [
            {
                "product_id": item["product_id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": item["quantity"],
                "total_price": item["quantity"] * item["price"]
            }
            for item in items
        ]

        return jsonify({"message": "Order retrieved successfully", "order": order}), 200
    finally:
        close_db_connection(connection)
