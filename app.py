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
            course TEXT NOT NULL,
            section TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# UI Page (HTML + JS + Peach + White Theme)
# -----------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Manager</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #FFE5B4; /* light peach */
            color: #4B2E2E; /* dark brown */
            padding: 40px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        .input-container {
            text-align: center;
            margin-bottom: 20px;
        }
        input {
            margin: 5px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #D9A066;
        }
        button {
            padding: 10px 15px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            background-color: #FFB07C; /* peach */
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #FFA15C;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            background-color: #FFFFFF; /* white table */
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: center;
        }
        th {
            background-color: #FFAD81; /* peach header */
            color: white;
        }
        tr:nth-child(even) {
            background-color: #FFF1E0; /* light peach row */
        }
        tr:hover {
            background-color: #FFD8B0;
        }
        #searchBar {
            width: 300px;
        }
    </style>
</head>
<body>

<h2>🎓 Student Manager</h2>

<div class="input-container">
    <input id="name" placeholder="Name">
    <input id="course" placeholder="Course">
    <input id="section" placeholder="Section">
    <button onclick="addStudent()">Add Student</button>
    <br>
    <input id="searchBar" placeholder="Search by name, course or section" oninput="filterStudents()">
    <button onclick="resetSearch()">Reset</button>
</div>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Course</th>
            <th>Section</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="studentTable"></tbody>
</table>

<script>
let allStudents = [];

const API = "/student";

function fetchStudents() {
    fetch(API)
    .then(res => res.json())
    .then(data => {
        allStudents = data;
        displayStudents(allStudents);
    });
}

function displayStudents(students) {
    let table = document.getElementById("studentTable");
    table.innerHTML = "";
    students.forEach(s => {
        table.innerHTML += `
            <tr>
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td>${s.course}</td>
                <td>${s.section}</td>
                <td>
                    <button onclick="editStudent(${s.id})">Edit</button>
                    <button onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            </tr>
        `;
    });
}

function addStudent() {
    let name = document.getElementById("name").value;
    let course = document.getElementById("course").value;
    let section = document.getElementById("section").value;

    fetch(API, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, course, section})
    }).then(() => {
        document.getElementById("name").value = "";
        document.getElementById("course").value = "";
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
    let course = prompt("Enter new course:");
    let section = prompt("Enter new section:");

    fetch(API + "/" + id, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, course, section})
    }).then(() => fetchStudents());
}

function filterStudents() {
    const term = document.getElementById("searchBar").value.toLowerCase();
    const filtered = allStudents.filter(s =>
        s.name.toLowerCase().includes(term) ||
        s.course.toLowerCase().includes(term) ||
        s.section.toLowerCase().includes(term)
    );
    displayStudents(filtered);
}

function resetSearch() {
    document.getElementById("searchBar").value = "";
    displayStudents(allStudents);
}

fetchStudents();
</script>

</body>
</html>
"""

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO students (name, course, section) VALUES (?, ?, ?)',
        (data['name'], data['course'], data['section'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Added"})

@app.route('/student', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])

@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name=?, course=?, section=? WHERE id=?',
        (data['name'], data['course'], data['section'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

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
