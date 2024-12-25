# Use the official MySQL image as the base
FROM mysql:8.0

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=ecommerce
ENV MYSQL_USER=ecom_user
ENV MYSQL_PASSWORD=ecom_password

# Copy SQL scripts to initialize the database
# These scripts will be executed automatically when the container is first started
COPY ./schema.sql /docker-entrypoint-initdb.d/schema.sql
COPY ./data.sql /docker-entrypoint-initdb.d/data.sql

# Expose the default MySQL port
EXPOSE 3306

# Default command to start MySQL
CMD ["mysqld"]
