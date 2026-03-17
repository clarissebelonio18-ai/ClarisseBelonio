from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# -----------------------------
# Database Functions
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Routes
# -----------------------------

# Home route
@app.route('/')
def home():
    return "Flask API is running! ✅"

# ➤ CREATE student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO students (name, grade, section) VALUES (?, ?, ?)',
            (data['name'], data['grade'], data['section'])
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Student added successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ➤ READ all students
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# ➤ READ single student
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# ➤ UPDATE student
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE students SET name=?, grade=?, section=? WHERE id=?',
        (data['name'], data['grade'], data['section'], id)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.close()
    return jsonify({"message": "Student updated successfully!"})


# ➤ DELETE student
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.close()
    return jsonify({"message": "Student deleted successfully!"})


# -----------------------------
# Run Server (IMPORTANT)
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
