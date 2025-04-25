from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mariadb"),
        user=os.getenv("MYSQL_USER", "user"),
        password=os.getenv("MYSQL_PASSWORD", "password"),
        database=os.getenv("MYSQL_DATABASE", "fido")
    )

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json()
        user = data.get("user", "user gibbetnet")
        message = data.get("message", "message gibbetnet")
        pin = data.get("pin", 1111)
        serial_number = data.get("serial_number", "message gibbetnet")


        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user, pin, serial_number, message) VALUES (%s, %s, %s, %s)", (user, pin, serial_number, message))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": f"Inserted {user} into database"}), 201

    return jsonify({"message": "Hello from /api"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
