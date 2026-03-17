from flask import Flask, jsonify, request, render_template_string
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
# UI Page (HTML + JS)
# -----------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Manager</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input { margin: 5px; padding: 8px; }
        button { padding: 8px; margin: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px;}
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center;}
        th { background-color: #f4f4f4; }
    </style>
</head>
<body>

<h2>🎓 Student Manager (CRUD)</h2>

<input id="name" placeholder="Name">
<input id="grade" placeholder="Grade" type="number">
<input id="section" placeholder="Section">
<button onclick="addStudent()">Add Student</button>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Grade</th>
            <th>Section</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="studentTable"></tbody>
</table>

<script>
const API = "/student";

function fetchStudents() {
    fetch(API)
    .then(res => res.json())
    .then(data => {
        let table = document.getElementById("studentTable");
        table.innerHTML = "";
        data.forEach(s => {
            table.innerHTML += `
                <tr>
                    <td>${s.id}</td>
                    <td>${s.name}</td>
                    <td>${s.grade}</td>
                    <td>${s.section}</td>
                    <td>
                        <button onclick="editStudent(${s.id})">Edit</button>
                        <button onclick="deleteStudent(${s.id})">Delete</button>
                    </td>
                </tr>
            `;
        });
    });
}

function addStudent() {
    let name = document.getElementById("name").value;
    let grade = document.getElementById("grade").value;
    let section = document.getElementById("section").value;

    fetch(API, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, grade, section})
    }).then(() => {
        document.getElementById("name").value = "";
        document.getElementById("grade").value = "";
        document.getElementById("section").value = "";
        fetchStudents();
    });
}

function deleteStudent(id) {
    fetch(API + "/" + id, { method: "DELETE" })
    .then(() => fetchStudents());
}

function editStudent(id) {
    let name = prompt("Enter new name:");
    let grade = prompt("Enter new grade:");
    let section = prompt("Enter new section:");

    fetch(API + "/" + id, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, grade, section})
    }).then(() => fetchStudents());
}

fetchStudents();
</script>

</body>
</html>
"""

# -----------------------------
# Routes
# -----------------------------

# UI Page
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# CREATE
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
    return jsonify({"message": "Added"})

# READ ALL
@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])

# UPDATE
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name=?, grade=?, section=? WHERE id=?',
        (data['name'], data['grade'], data['section'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

# DELETE
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

# -----------------------------
# Run
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
