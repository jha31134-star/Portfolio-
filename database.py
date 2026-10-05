import sqlite3


DATABASE_NAME = "hospital.db"


# =========================================================
# CONNECT TO DATABASE
# =========================================================

def connect():
    return sqlite3.connect(DATABASE_NAME)


# =========================================================
# CREATE PATIENT TABLE
# =========================================================

def create_tables():

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            blood_group TEXT,
            allergies TEXT,
            symptoms TEXT,
            department TEXT,
            doctor TEXT,
            room TEXT,
            bed_number TEXT
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# ADD / UPDATE PATIENT
# =========================================================

def add_patient(data):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO patients
        (
            patient_id,
            name,
            age,
            gender,
            blood_group,
            allergies,
            symptoms,
            department,
            doctor,
            room,
            bed_number
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    connection.commit()
    connection.close()


# =========================================================
# GET ALL PATIENTS
# =========================================================

def get_patients():

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            patient_id,
            name,
            age,
            gender,
            blood_group,
            allergies,
            symptoms,
            department,
            doctor,
            room,
            bed_number
        FROM patients
        ORDER BY patient_id
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows