from database.db_config import get_db_connection, close_db_connection
from models.product import Product


class Order:
    def __init__(self, order_id, user_id, total_amount, items):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.items = items  # List of Product objects

    def to_dict(self):
        """Convert Order object to dictionary for JSON serialization."""
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "total_amount": self.total_amount,
            "items": [item.to_dict() for item in self.items]
        }

    @staticmethod
    def create_order(user_id, total_amount, items):
        """
        Save a new order to the database.
        Args:
            user_id: ID of the user placing the order.
            total_amount: Total amount of the order.
            items: List of dictionaries with product_id and quantity.
        Returns:
            The created order as an Order object.
        """
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        try:
            cursor = connection.cursor()

            # Insert the order into the orders table
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)",
                (user_id, total_amount),
            )
            order_id = cursor.lastrowid

            # Insert each item into the order_items table
            for item in items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, item["product_id"], item["quantity"]),
                )

            connection.commit()

            # Create Product objects for the items
            product_objects = [
                Product.get_product_by_id(item["product_id"]) for item in items
            ]

            return Order(order_id=order_id, user_id=user_id, total_amount=total_amount, items=product_objects)

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            close_db_connection(connection)

    @staticmethod
    def get_order_by_id(order_id):
        """
        Retrieve an order by its ID from the database.
        Args:
            order_id: ID of the order to retrieve.
        Returns:
            An Order object if found, else None.
        """
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        try:
            cursor = connection.cursor(dictionary=True)

            # Fetch the order details
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order_row = cursor.fetchone()

            if not order_row:
                return None

            # Fetch the items associated with the order
            cursor.execute(
                "SELECT oi.product_id, oi.quantity, p.name, p.price "
                "FROM order_items oi "
                "JOIN products p ON oi.product_id = p.id "
                "WHERE oi.order_id = %s",
                (order_id,),
            )
            items = cursor.fetchall()

            # Create Product objects for the items
            product_objects = [
                Product(product_id=item["product_id"], name=item["name"], price=item["price"])
                for item in items
            ]

            return Order(
                order_id=order_row["id"],
                user_id=order_row["user_id"],
                total_amount=order_row["total_amount"],
                items=product_objects,
            )

        finally:
            close_db_connection(connection)
