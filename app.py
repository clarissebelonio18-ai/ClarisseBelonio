from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# -----------------------------
# Database Initialization
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

@app.route('/')
def home():
    return "Welcome to my Flask API with Database!"

# ➤ CREATE student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO students (name, grade, section) VALUES (?, ?, ?)',
        (data['name'], data['grade'], data['section'])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully!"})

# ➤ READ all students
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    result = []
    for student in students:
        result.append({
            "id": student["id"],
            "name": student["name"],
            "grade": student["grade"],
            "section": student["section"]
        })

    return jsonify(result)

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

    return jsonify({
        "id": student["id"],
        "name": student["name"],
        "grade": student["grade"],
        "section": student["section"]
    })

# ➤ UPDATE student
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name = ?, grade = ?, section = ? WHERE id = ?',
        (data['name'], data['grade'], data['section'], id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Student updated successfully!"})

# ➤ DELETE student
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully!"})

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
