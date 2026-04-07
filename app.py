print("Hostel Management System")
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
    print(f"{'ID':<4} {'Name':<15} {'Phone':<12} {'Course':<10} {'Room':<5} {'Fee':<8}")
    print("-" * 60)
    for s in students:
        print(f"{s[0]:<4} {s[1]:<15} {s[2]:<12} {s[3]:<10} {s[4]:<5} {s[5]:<8}")

def view_rooms():
    print("\n--- Room Status ---")
    cursor.execute("SELECT * FROM rooms ORDER BY room_no")
    rooms = cursor.fetchall()
    print(f"{'Room':<6} {'Type':<12} {'Capacity':<10} {'Occupied':<10} {'Available':<10}")
    print("-" * 55)
    for r in rooms:
        available = r[2] - r[3]
        print(f"{r[0]:<6} {r[1]:<12} {r[2]:<10} {r[3]:<10} {available:<10}")

def pay_fee():
    print("\n--- Fee Payment ---")
    student_id = int(input("Enter Student ID: "))
    cursor.execute("SELECT name, fee_status FROM students WHERE student_id=?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found!")
        return
    if student[1] == 'Paid':
        print(f"Fee already paid for {student[0]}")
        return
    
    amount = float(input("Enter Amount: "))
    pay_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO fees (student_id, amount, pay_date, status) VALUES (?, ?, ?, ?)",
                   (student_id, amount, pay_date, 'Paid'))
    cursor.execute("UPDATE students SET fee_status='Paid' WHERE student_id=?", (student_id,))
    conn.commit()
    print(f"Fee of Rs.{amount} paid for {student[0]}. Receipt generated.")

def delete_student():
    print("\n--- Vacate Student ---")
    student_id = int(input("Enter Student ID to vacate: "))
    cursor.execute("SELECT name, room_no FROM students WHERE student_id=?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found!")
        return
    
    cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    cursor.execute("UPDATE rooms SET occupied = occupied - 1 WHERE room_no=?", (student[1],))
    conn.commit()
    print(f"Student {student[0]} vacated from Room {student[1]}")

def main_menu():
    while True:
        print("\n====== HOSTEL MANAGEMENT SYSTEM ======")
        print("1. Add Student")
        print("2. View All Students") 
        print("3. View Room Status")
        print("4. Pay Fee")
        print("5. Vacate Student")
        print("6. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1': add_student()
        elif choice == '2': view_students()
        elif choice == '3': view_rooms()
        elif choice == '4': pay_fee()
        elif choice == '5': delete_student()
        elif choice == '6': 
            print("Exiting...")
            break
        else: print("Invalid choice!")

if __name__ == "__main__":
    main_menu()
    conn.close()