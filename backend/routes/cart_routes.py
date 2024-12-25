from flask import Blueprint, request, jsonify
from database.db_config import get_db_connection, close_db_connection

cart_bp = Blueprint('cart', __name__)

# GET: Fetch all items in the cart
@cart_bp.route('/cart', methods=['GET'])
def get_cart():
    """
    Fetch all items in the cart for a given user.
    Expects 'user_id' as a query parameter.
    """
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "Missing 'user_id' parameter"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT c.product_id, c.quantity, p.name, p.price
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """
        cursor.execute(query, (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({"message": "Cart is empty", "cart_items": []}), 200

        response = [
            {
                "product_id": item["product_id"],
                "name": item["name"],
                "price": float(item["price"]),
                "quantity": item["quantity"],
                "total_price": round(item["quantity"] * float(item["price"]), 2),
            }
            for item in cart_items
        ]

        return jsonify({"message": "Cart items retrieved successfully", "cart_items": response}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve cart items", "error": str(e)}), 500
    finally:
        close_db_connection(connection)

# POST: Add a product to the cart
@cart_bp.route('/cart', methods=['POST'])
def add_to_cart():
    """
    Add a product to the cart for a given user.
    Expects JSON payload: { user_id, product_id, quantity }.
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not user_id or not product_id:
            return jsonify({"message": "'user_id' and 'product_id' are required"}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({"message": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)
        # Check if the product already exists in the cart
        check_query = """
            SELECT quantity FROM cart_items WHERE user_id = %s AND product_id = %s
        """
        cursor.execute(check_query, (user_id, product_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update the quantity
            new_quantity = existing_item["quantity"] + quantity
            update_query = """
                UPDATE cart_items SET quantity = %s WHERE user_id = %s AND product_id = %s
            """
            cursor.execute(update_query, (new_quantity, user_id, product_id))
        else:
            # Insert new item into the cart
            insert_query = """
                INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, product_id, quantity))

        connection.commit()
        return jsonify({"message": "Product added to cart successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add product to cart", "error": str(e)}), 500
    finally:
        close_db_connection(connection)

# DELETE: Remove a product from the cart
@cart_bp.route('/cart', methods=['DELETE'])
def remove_from_cart():
    """
    Remove a product from the cart for a given user.
    Expects JSON payload: { user_id, product_id }.
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')

        if not user_id or not product_id:
            return jsonify({"message": "'user_id' and 'product_id' are required"}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({"message": "Database connection failed"}), 500

        cursor = connection.cursor()
        delete_query = """
            DELETE FROM cart_items WHERE user_id = %s AND product_id = %s
        """
        cursor.execute(delete_query, (user_id, product_id))

        if cursor.rowcount == 0:
            return jsonify({"message": "Product not found in cart"}), 404

        connection.commit()
        return jsonify({"message": "Product removed from cart successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to remove product from cart", "error": str(e)}), 500
    finally:
        close_db_connection(connection)
