CREATE DATABASE hostel_db;
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('hostel.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    course TEXT,
    room_no INTEGER,
    join_date TEXT,
    fee_status TEXT DEFAULT 'Unpaid'
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    room_no INTEGER PRIMARY KEY,
    room_type TEXT,
    capacity INTEGER,
    occupied INTEGER DEFAULT 0
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS fees (
    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount REAL,
    pay_date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)''')
conn.commit()

# Initialize 10 rooms if empty
cursor.execute("SELECT COUNT(*) FROM rooms")
if cursor.fetchone()[0] == 0:
    rooms_data = [
        (101, '2-Sharing', 2), (102, '2-Sharing', 2), (103, '3-Sharing', 3),
        (104, '2-Sharing', 2), (105, '3-Sharing', 3), (201, '2-Sharing', 2),
        (202, '3-Sharing', 3), (203, '2-Sharing', 2), (204, '3-Sharing', 3),
        (205, '1-Sharing', 1)
    ]
    cursor.executemany("INSERT INTO rooms (room_no, room_type, capacity) VALUES (?, ?, ?)", rooms_data)
    conn.commit()

def add_student():
    print("\n--- Add New Student ---")
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    course = input("Course: ")
    
    # Show available rooms
    cursor.execute("SELECT room_no, room_type, capacity, occupied FROM rooms WHERE occupied < capacity")
    available = cursor.fetchall()
    if not available:
        print("No rooms available!")
        return
    
    print("\nAvailable Rooms:")
    for r in available:
        print(f"Room {r[0]} | {r[1]} | {r[3]}/{r[2]} occupied")
    
    room_no = int(input("Enter Room No to allocate: "))
    
    # Check room capacity
    cursor.execute("SELECT capacity, occupied FROM rooms WHERE room_no=?", (room_no,))
    room = cursor.fetchone()
    if not room or room[1] >= room[0]:
        print("Invalid room or room full!")
        return
    
    join_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO students (name, phone, email, course, room_no, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, phone, email, course, room_no, join_date))
    cursor.execute("UPDATE rooms SET occupied = occupied + 1 WHERE room_no=?", (room_no,))
    conn.commit()
    print(f"Student {name} added successfully to Room {room_no}!")

def view_students():
    print("\n--- All Students ---")
    cursor.execute('''
        SELECT s.student_id, s.name, s.phone, s.course, s.room_no, s.fee_status 
        FROM students s ORDER BY s.student_id
    ''')
    students = cursor.fetchall()
    if not students:
        print("No students found.")
        return
    print(f"{'ID':<4} {'Name':<15} {'Phone':<12} {'Course':<10} {'