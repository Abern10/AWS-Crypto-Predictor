import mysql.connector

def query_raw_data():
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = db.cursor()

    cursor.execute("SELECT * FROM raw_data LIMIT 10")
    results = cursor.fetchall()

    for row in results:
        print(row)
    
    cursor.close()
    db.close()

if __name__ == "__main__":
    query_raw_data()