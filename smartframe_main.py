import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from frame_engine import Frame


# =========================================================
# DATABASE
# =========================================================

DATABASE_NAME = "hospital.db"


def connect():
    return sqlite3.connect(DATABASE_NAME)


def create_database():

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            phone TEXT,
            address TEXT,
            blood_group TEXT,
            allergies TEXT,
            symptoms TEXT,
            department TEXT,
            doctor TEXT,
            room TEXT,
            bed_number TEXT
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(patients)")

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # Add missing columns to old database
    required_columns = {
        "gender": "TEXT",
        "phone": "TEXT",
        "address": "TEXT",
        "blood_group": "TEXT",
        "allergies": "TEXT",
        "symptoms": "TEXT",
        "department": "TEXT",
        "doctor": "TEXT",
        "room": "TEXT",
        "bed_number": "TEXT"
    }

    for column, data_type in required_columns.items():

        if column not in columns:

            cursor.execute(
                f"ALTER TABLE patients ADD COLUMN {column} {data_type}"
            )

    connection.commit()
    connection.close()


# Create database when program starts
create_database()


# =========================================================
# SAVE PATIENT TO DATABASE
# =========================================================

def save_to_database(data):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO patients
        (
            patient_id,
            name,
            age,
            gender,
            phone,
            address,
            blood_group,
            allergies,
            symptoms,
            department,
            doctor,
            room,
            bed_number
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    connection.commit()
    connection.close()


# =========================================================
# GET ONE PATIENT
# =========================================================

def find_patient(patient_id):

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            patient_id,
            name,
            age,
            gender,
            phone,
            address,
            blood_group,
            allergies,
            symptoms,
            department,
            doctor,
            room,
            bed_number
        FROM patients
        WHERE LOWER(patient_id) = LOWER(?)
    """, (patient_id,))

    result = cursor.fetchone()

    connection.close()

    return result


# =========================================================
# GET ALL PATIENTS
# =========================================================

def get_all_patients():

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            patient_id,
            name,
            age,
            gender,
            phone,
            address,
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

    results = cursor.fetchall()

    connection.close()

    return results


# =========================================================
# FRAME-BASED KNOWLEDGE REPRESENTATION
# =========================================================

person = Frame("PERSON")

person.set_slot(
    "Phone",
    "Not Provided"
)

person.set_slot(
    "Address",
    "Not Provided"
)


patient_template = Frame(
    "PATIENT",
    person
)


patient_template.set_slot(
    "Patient ID",
    "Not Assigned"
)

patient_template.set_slot(
    "Name",
    "Not Provided"
)

patient_template.set_slot(
    "Age",
    "Not Provided"
)

patient_template.set_slot(
    "Gender",
    "Not Provided"
)

patient_template.set_slot(
    "Blood Group",
    "Unknown"
)

patient_template.set_slot(
    "Allergies",
    "Not Provided"
)

patient_template.set_slot(
    "Symptoms",
    "None"
)

patient_template.set_slot(
    "Department",
    "General Medicine"
)

patient_template.set_slot(
    "Doctor",
    "Not Assigned"
)

patient_template.set_slot(
    "Room",
    "Not Assigned"
)

patient_template.set_slot(
    "Bed Number",
    "Not Assigned"
)


# =========================================================
# KNOWLEDGE BASE
# =========================================================

knowledge = {

    "General Medicine": {
        "fever",
        "cough",
        "sore throat"
    },

    "Neurology": {
        "headache",
        "dizziness",
        "migraine"
    },

    "Orthopedics": {
        "joint pain",
        "bone pain",
        "swelling"
    },

    "Gastroenterology": {
        "stomach pain",
        "vomiting",
        "diarrhea"
    }

}


# =========================================================
# REASONING
# =========================================================

def suggest_department(symptoms):

    symptom_set = {
        item.strip().lower()
        for item in symptoms.split(",")
        if item.strip()
    }

    best_department = "General Medicine"
    highest_score = 0

    for department, known_symptoms in knowledge.items():

        score = len(
            symptom_set.intersection(
                known_symptoms
            )
        )

        if score > highest_score:

            highest_score = score
            best_department = department

    return best_department


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "SMARTFRAME HOSPITAL"
)

root.geometry(
    "1200x750"
)


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(root)

header.pack(
    fill="x",
    pady=10
)


tk.Label(
    header,
    text="SMARTFRAME HOSPITAL",
    font=("Arial", 26, "bold")
).pack()


tk.Label(
    header,
    text="Hospital Management System using Frame-Based Knowledge Representation",
    font=("Arial", 11)
).pack()


# =========================================================
# TABS
# =========================================================

notebook = ttk.Notebook(root)

notebook.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)


# =========================================================
# PATIENT MANAGEMENT TAB
# =========================================================

patient_tab = ttk.Frame(notebook)

notebook.add(
    patient_tab,
    text="Patient Management"
)


form = ttk.LabelFrame(
    patient_tab,
    text="Patient Details"
)

form.pack(
    fill="x",
    padx=20,
    pady=20
)


fields = [

    "Patient ID",
    "Name",
    "Age",
    "Gender",
    "Phone Number",
    "Address",
    "Blood Group",
    "Allergies",
    "Symptoms",
    "Doctor",
    "Room",
    "Bed Number"

]


entries = {}


for row, field in enumerate(fields):

    ttk.Label(
        form,
        text=field + ":"
    ).grid(
        row=row,
        column=0,
        padx=15,
        pady=5,
        sticky="w"
    )

    entry = ttk.Entry(
        form,
        width=45
    )

    entry.grid(
        row=row,
        column=1,
        padx=15,
        pady=5
    )

    entries[field] = entry


# =========================================================
# SAVE PATIENT
# =========================================================

def save_patient():

    patient_id = entries["Patient ID"].get().strip()
    name = entries["Name"].get().strip()
    age_text = entries["Age"].get().strip()
    gender = entries["Gender"].get().strip()
    phone = entries["Phone Number"].get().strip()
    address = entries["Address"].get().strip()
    blood_group = entries["Blood Group"].get().strip()
    allergies = entries["Allergies"].get().strip()
    symptoms = entries["Symptoms"].get().strip()
    doctor = entries["Doctor"].get().strip()
    room = entries["Room"].get().strip()
    bed_number = entries["Bed Number"].get().strip()


    # Validation

    if patient_id == "":
        messagebox.showerror(
            "Error",
            "Enter Patient ID."
        )
        return


    if name == "":
        messagebox.showerror(
            "Error",
            "Enter Patient Name."
        )
        return


    if age_text == "":
        messagebox.showerror(
            "Error",
            "Enter Age."
        )
        return


    try:
        age = int(age_text)

    except ValueError:
        messagebox.showerror(
            "Error",
            "Age must be a number."
        )
        return


    # Default values

    if gender == "":
        gender = "Not Provided"

    if phone == "":
        phone = "Not Provided"

    if address == "":
        address = "Not Provided"

    if blood_group == "":
        blood_group = "Unknown"

    if allergies == "":
        allergies = "Not Provided"

    if symptoms == "":
        symptoms = "None"

    if doctor == "":
        doctor = "Not Assigned"

    if room == "":
        room = "Not Assigned"

    if bed_number == "":
        bed_number = "Not Assigned"


    # Department suggestion

    if symptoms.lower() == "none":

        department = "General Medicine"

    else:

        department = suggest_department(
            symptoms
        )


    # =====================================================
    # CREATE PATIENT FRAME
    # =====================================================

    patient_frame = Frame(
        "PATIENT_" + patient_id,
        patient_template
    )


    patient_frame.set_slot(
        "Patient ID",
        patient_id
    )

    patient_frame.set_slot(
        "Name",
        name
    )

    patient_frame.set_slot(
        "Age",
        age
    )

    patient_frame.set_slot(
        "Gender",
        gender
    )

    patient_frame.set_slot(
        "Phone",
        phone
    )

    patient_frame.set_slot(
        "Address",
        address
    )

    patient_frame.set_slot(
        "Blood Group",
        blood_group
    )

    patient_frame.set_slot(
        "Allergies",
        allergies
    )

    patient_frame.set_slot(
        "Symptoms",
        symptoms
    )

    patient_frame.set_slot(
        "Department",
        department
    )

    patient_frame.set_slot(
        "Doctor",
        doctor
    )

    patient_frame.set_slot(
        "Room",
        room
    )

    patient_frame.set_slot(
        "Bed Number",
        bed_number
    )


    # =====================================================
    # EXACTLY 13 VALUES
    # =====================================================

    data = (

        patient_id,
        name,
        age,
        gender,
        phone,
        address,
        blood_group,
        allergies,
        symptoms,
        department,
        doctor,
        room,
        bed_number

    )


    # Save

    try:

        save_to_database(data)

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )

        return


    # Success

    messagebox.showinfo(
        "Success",
        "Patient details saved successfully!"
    )


    # Clear fields

    for entry in entries.values():

        entry.delete(
            0,
            tk.END
        )


# =========================================================
# SAVE BUTTON
# =========================================================

ttk.Button(
    patient_tab,
    text="SAVE PATIENT",
    command=save_patient
).pack(
    pady=10
)


# =========================================================
# SEARCH PATIENT TAB
# =========================================================

search_tab = ttk.Frame(notebook)

notebook.add(
    search_tab,
    text="Search Patient"
)


search_box = ttk.LabelFrame(
    search_tab,
    text="Enter Patient ID"
)

search_box.pack(
    fill="x",
    padx=20,
    pady=20
)


ttk.Label(
    search_box,
    text="Patient ID:"
).grid(
    row=0,
    column=0,
    padx=15,
    pady=15
)


search_entry = ttk.Entry(
    search_box,
    width=40
)

search_entry.grid(
    row=0,
    column=1,
    padx=15,
    pady=15
)


search_output = tk.Text(
    search_tab,
    font=("Courier", 11)
)

search_output.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# =========================================================
# SEARCH FUNCTION
# =========================================================

def search_patient():

    patient_id = search_entry.get().strip()

    search_output.delete(
        "1.0",
        tk.END
    )


    if patient_id == "":

        messagebox.showwarning(
            "Search",
            "Enter Patient ID."
        )

        return


    patient = find_patient(
        patient_id
    )


    if patient is None:

        search_output.insert(
            tk.END,
            "PATIENT NOT FOUND"
        )

        return


    search_output.insert(
        tk.END,
        "PATIENT INFORMATION\n"
    )

    search_output.insert(
        tk.END,
        "=" * 70 + "\n\n"
    )


    information = [

        ("Patient ID", patient[0]),
        ("Name", patient[1]),
        ("Age", patient[2]),
        ("Gender", patient[3]),
        ("Phone Number", patient[4]),
        ("Address", patient[5]),
        ("Blood Group", patient[6]),
        ("Allergies", patient[7]),
        ("Symptoms", patient[8]),
        ("Department", patient[9]),
        ("Doctor", patient[10]),
        ("Room", patient[11]),
        ("Bed Number", patient[12])

    ]


    for label, value in information:

        search_output.insert(
            tk.END,
            f"{label:<20}: {value}\n"
        )


# =========================================================
# SEARCH BUTTON
# =========================================================

ttk.Button(
    search_box,
    text="SEARCH",
    command=search_patient
).grid(
    row=0,
    column=2,
    padx=15,
    pady=15
)


# =========================================================
# FRAME EXPLORER
# =========================================================

frame_tab = ttk.Frame(notebook)

notebook.add(
    frame_tab,
    text="Frame Explorer"
)


frame_output = tk.Text(
    frame_tab,
    font=("Courier", 11)
)

frame_output.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)


def show_frames():

    frame_output.delete(
        "1.0",
        tk.END
    )


    frame_output.insert(
        tk.END,
        "SMARTFRAME KNOWLEDGE STRUCTURE\n"
    )

    frame_output.insert(
        tk.END,
        "=" * 70 + "\n\n"
    )


    frame_output.insert(
        tk.END,
        "FRAME 1: PERSON\n"
    )

    frame_output.insert(
        tk.END,
        "-" * 30 + "\n"
    )


    for slot, value in person.all_slots().items():

        frame_output.insert(
            tk.END,
            f"{slot:<20}: {value}\n"
        )


    frame_output.insert(
        tk.END,
        "\nFRAME 2: PATIENT\n"
    )

    frame_output.insert(
        tk.END,
        "-" * 30 + "\n"
    )

    frame_output.insert(
        tk.END,
        "Parent Frame : PERSON\n\n"
    )


    for slot, value in patient_template.all_slots().items():

        frame_output.insert(
            tk.END,
            f"{slot:<20}: {value}\n"
        )


    frame_output.insert(
        tk.END,
        "\n\nFRAME HIERARCHY\n"
    )

    frame_output.insert(
        tk.END,
        "=" * 50 + "\n\n"
    )

    frame_output.insert(
        tk.END,
        "PERSON\n"
    )

    frame_output.insert(
        tk.END,
        "  |\n"
    )

    frame_output.insert(
        tk.END,
        "  +---- PATIENT\n"
    )

    frame_output.insert(
        tk.END,
        "           |\n"
    )

    frame_output.insert(
        tk.END,
        "           +---- Patient Instance\n"
    )


    frame_output.insert(
        tk.END,
        "\n\nMEDICAL KNOWLEDGE FRAMES\n"
    )

    frame_output.insert(
        tk.END,
        "=" * 50 + "\n\n"
    )


    for department, symptoms in knowledge.items():

        frame_output.insert(
            tk.END,
            department + "\n"
        )

        frame_output.insert(
            tk.END,
            "  Symptoms: "
            + ", ".join(sorted(symptoms))
            + "\n\n"
        )


ttk.Button(
    frame_tab,
    text="LOAD FRAME KNOWLEDGE",
    command=show_frames
).pack(
    pady=10
)


# =========================================================
# ALL PATIENTS
# =========================================================

all_tab = ttk.Frame(notebook)

notebook.add(
    all_tab,
    text="All Patients"
)


all_output = tk.Text(
    all_tab,
    font=("Courier", 10)
)

all_output.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


def load_all_patients():

    all_output.delete(
        "1.0",
        tk.END
    )


    patients = get_all_patients()


    if not patients:

        all_output.insert(
            tk.END,
            "No patient records found."
        )

        return


    all_output.insert(
        tk.END,
        "ALL PATIENT RECORDS\n"
    )

    all_output.insert(
        tk.END,
        "=" * 100 + "\n\n"
    )


    for patient in patients:

        information = [

            ("Patient ID", patient[0]),
            ("Name", patient[1]),
            ("Age", patient[2]),
            ("Gender", patient[3]),
            ("Phone Number", patient[4]),
            ("Address", patient[5]),
            ("Blood Group", patient[6]),
            ("Allergies", patient[7]),
            ("Symptoms", patient[8]),
            ("Department", patient[9]),
            ("Doctor", patient[10]),
            ("Room", patient[11]),
            ("Bed Number", patient[12])

        ]


        for label, value in information:

            all_output.insert(
                tk.END,
                f"{label:<20}: {value}\n"
            )


        all_output.insert(
            tk.END,
            "-" * 100 + "\n\n"
        )


ttk.Button(
    all_tab,
    text="LOAD ALL PATIENTS",
    command=load_all_patients
).pack(
    pady=10
)


# =========================================================
# START
# =========================================================

root.mainloop()