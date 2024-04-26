from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'my_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

def connect_to_database():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received data:", data)

    # Insert data into PostgreSQL database
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO \"system_test\" (temp, ph) VALUES (%s, %s)", (data['temp'], data['ph']))
        conn.commit()
        cursor.close()
        conn.close()
        return "Data received and inserted into database successfully\n"
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return f"Error: {str(e)}\n", 500


@app.route('/pull_data', methods=['GET'])
def pull_data():
    # data = request.get_json()
    # print("Received data:", data)

    # Insert data into PostgreSQL database
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT temp, ph FROM \"system_test\" ORDER BY timestamp DESC LIMIT 1;")
        data = cursor.fetchone()  # Fetch one row from the result set
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify(data), 200  # Return the retrieved data as JSON
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return f"Error: {str(e)}\n", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')