from dotenv import load_dotenv
import os
import pymysql

# Get database details from file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Assuming default port is 5432 if not specified
db_port_str = os.environ.get("DB_PORT", "5432")

# Validate and convert to integer
try:
    db_port = int(db_port_str)
except ValueError:
    print(f"Error: Invalid DB_PORT value: {db_port_str}")
    # Handle the error or set a default value as needed
    db_port = 5432  # Default portf
db_config = {
    "host": os.environ.get("DB_HOST"),
    "port": db_port,
    "user": os.environ.get("DB_USERNAME"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
}

class Table:
    def __init__(self, table_name):
        self.table_name = table_name

    def query(self, columns="*", condition=None, order_by=None):
        # Make a connection
        with pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        ) as connection:
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # Prepare SQL statement for querying data
            query = f"SELECT {columns} FROM {self.table_name}"
            if condition:
                query += f" WHERE {condition}"
            if order_by:
                query += f" ORDER BY {order_by}"

            # Execute query and return results
            cursor.execute(query)
            result = cursor.fetchall()

        return result

    def add_entry(self, data):
        with pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        ) as connection:
            cursor = connection.cursor()

            # Construct the INSERT query
            columns = ", ".join(data.keys())
            values = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})"

            try:
                # Execute SQL
                cursor.execute(query, tuple(data.values()))
                connection.commit()
            except pymysql.IntegrityError:
                # Handle integrity constraint violations
                connection.rollback()

    def edit_entry(self, update_data, condition, additional_condition=None):
        with pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        ) as connection:
            cursor = connection.cursor()

            # Construct the UPDATE query
            query = f"UPDATE {self.table_name} SET "
            set_values = ", ".join([f"{column} = %s" for column in update_data.keys()])
            query += set_values + f" WHERE {condition}"

            # Add an optional additional condition
            if additional_condition:
                query += f" AND {additional_condition}"

            # Execute the query
            cursor.execute(query, tuple(update_data.values()))
            connection.commit()

    def remove_entry(self, condition):
        with pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        ) as connection:
            cursor = connection.cursor()

            # Construct the DELETE query
            query = f"DELETE FROM {self.table_name} WHERE {condition}"

            # Execute the query
            cursor.execute(query)
            connection.commit()
