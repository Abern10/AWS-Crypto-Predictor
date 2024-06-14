import mysql.connector
from mysql.connector import errorcode

# Database configuration
config = {
    'user': 'abern8',
    'password': 'JettaGLI17!',
    'host': 'cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
    'database': 'crypto_db',
    'raise_on_warnings': True
}

try:
    # Establishing the connection
    conn = mysql.connector.connect(**config)
    print("Database connection successful.")

    # Create a cursor object
    cursor = conn.cursor()

    # Testing a simple query
    cursor.execute("SELECT 1")

    # Fetch the result to ensure all results are read
    result = cursor.fetchall()
    print("Query result:", result)

    # Close the cursor
    cursor.close()

    # Close the connection
    conn.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(f"Database connection failed: {err}")