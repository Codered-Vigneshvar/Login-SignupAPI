from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# Database connection details
DB_HOST = "yt-demo.c7s8gqgmm3ln.us-east-2.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "G7m!X9t#qK2f5B&z4L"
DB_PORT = 5432

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# Create the notes table if it doesn't exist
def create_notes_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            note_text TEXT NOT NULL,
            note_key VARCHAR(120) NOT NULL UNIQUE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_notes_table()

@app.route("/")
def home():
    return "Welcome to the Notes API"

@app.route("/save-note", methods=["POST"])
def save_note():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "Request body must be JSON"}), 400

        note_text = data.get('note_text')
        note_key = data.get('note_key')

        if not note_text or not note_key:
            return jsonify({"message": "Missing required fields!"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO notes (note_text, note_key)
            VALUES (%s, %s)
        """)
        cur.execute(insert_query, (note_text, note_key))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Note saved successfully!"}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"message": "Note key already exists!"}), 400
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e)}), 500

@app.route("/get-note", methods=["POST"])
def get_note():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "Request body must be JSON"}), 400

        note_key = data.get('note_key')

        if not note_key:
            return jsonify({"message": "Missing required field: note_key"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        select_query = sql.SQL("""
            SELECT note_text FROM notes WHERE note_key = %s
        """)
        cur.execute(select_query, (note_key,))
        note = cur.fetchone()
        cur.close()
        conn.close()

        if note:
            return jsonify({"note_text": note[0]}), 200
        else:
            return jsonify({"message": "Note not found!"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
    
    #TEXT,PY