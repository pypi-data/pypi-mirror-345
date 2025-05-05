code = """
#Q1

import sqlite3

# Connect to the database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Create the employee table
cursor.execute('''
CREATE TABLE IF NOT EXISTS EmployeeDetails (
    EmpID INTEGER PRIMARY KEY,
    EmpName TEXT NOT NULL,
    Photo BLOB,
    Resume BLOB
)
''')

conn.commit()
print("EmployeeDetails table created successfully!")



def convert_to_binary(filename):
    # Open the file in binary read mode
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data



def insert_employee(emp_id, emp_name, photo_path, resume_path):
    # Ensure employee name starts with capital letter
    emp_name = emp_name.capitalize()

    # Convert photo and resume to binary
    photo_data = convert_to_binary(photo_path)
    resume_data = convert_to_binary(resume_path)

    # Insert the data into the table
    cursor.execute('''
    INSERT INTO EmployeeDetails (EmpID, EmpName, Photo, Resume)
    VALUES (?, ?, ?, ?)
    ''', (emp_id, emp_name, photo_data, resume_data))

    conn.commit()
    print(f"Employee {emp_name} added successfully!")



# Insert sample employees
insert_employee(1, 'alice', 'alice_photo.jpg', 'alice_resume.pdf')
insert_employee(2, 'bob', 'bob_photo.jpg', 'bob_resume.pdf')
insert_employee(3, 'charlie', 'charlie_photo.jpg', 'charlie_resume.pdf')


def retrieve_employee(emp_id):
    cursor.execute('''
    SELECT EmpID, EmpName, Photo, Resume
    FROM EmployeeDetails
    WHERE EmpID = ?
    ''', (emp_id,))
    
    record = cursor.fetchone()
    
    if record:
        id, name, photo_data, resume_data = record
        print(f"Employee ID: {id}")
        print(f"Employee Name: {name}")

        # Write photo
        with open(f"{name}_photo.jpg", 'wb') as file:
            file.write(photo_data)
        print(f"Photo saved as {name}_photo.jpg")
        
        # Write resume
        with open(f"{name}_resume.pdf", 'wb') as file:
            file.write(resume_data)
        print(f"Resume saved as {name}_resume.pdf")
    else:
        print(f"No employee found with ID {emp_id}")




#Q2  hospital

import sqlite3

# Connect or create database
conn = sqlite3.connect('HospitalManagement.db')
cursor = conn.cursor()

# 1. Create Hospital table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Hospital (
    Hospital_Id INTEGER PRIMARY KEY,
    Hospital_Name TEXT NOT NULL,
    Bed_Count INTEGER
)
''')

# 2. Create Doctor table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Doctor (
    Doctor_Id INTEGER PRIMARY KEY,
    Doctor_Name TEXT NOT NULL,
    Hospital_Id INTEGER,
    Joining_Date TEXT,
    Speciality TEXT,
    Salary INTEGER,
    Experience TEXT,
    FOREIGN KEY (Hospital_Id) REFERENCES Hospital(Hospital_Id)
)
''')

# Insert data into Hospital table
hospital_data = [
    (1, 'Mayo Clinic', 200),
    (2, 'Cleveland Clinic', 400),
    (3, 'Johns Hopkins', 1000),
    (4, 'UCLA Medical Center', 1500)
]

cursor.executemany('''
INSERT OR IGNORE INTO Hospital (Hospital_Id, Hospital_Name, Bed_Count)
VALUES (?, ?, ?)
''', hospital_data)

# Insert data into Doctor table
doctor_data = [
    (101, 'David', 1, '2005-02-10', 'Pediatric', 40000, None),
    (102, 'Michael', 1, '2015-07-23', 'Oncologist', 20000, None),
    (103, 'Susan', 2, '2016-05-19', 'Pharmacologist', 25000, None),
    (104, 'Robert', 2, '2017-12-28', 'Pediatric', 28000, None),
    (105, 'Linda', 3, '2004-06-04', 'Pharmacologist', 42000, None),
    (106, 'William', 3, '2012-09-11', 'Dermatologist', 30000, None),
    (107, 'Richard', 4, '2014-08-21', 'Pharmacologist', 32000, None),
    (108, 'Karen', 4, '2011-10-17', 'Radiologist', 30000, None)
]

cursor.executemany('''
INSERT OR IGNORE INTO Doctor (Doctor_Id, Doctor_Name, Hospital_Id, Joining_Date, Speciality, Salary, Experience)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', doctor_data)

conn.commit()

# Function to fetch hospital details
def get_hospital_details(hospital_id):
    cursor.execute('SELECT * FROM Hospital WHERE Hospital_Id = ?', (hospital_id,))
    result = cursor.fetchone()
    if result:
        print("\nPrinting Hospital record")
        print(f"Hospital Id: {result[0]}")
        print(f"Hospital Name: {result[1]}")
        print(f"Bed Count: {result[2]}")
    else:
        print("No Hospital found with this ID.")

# Function to fetch doctor details
def get_doctor_details(doctor_id):
    cursor.execute('SELECT * FROM Doctor WHERE Doctor_Id = ?', (doctor_id,))
    result = cursor.fetchone()
    if result:
        print("\nPrinting Doctor record")
        print(f"Doctor Id: {result[0]}")
        print(f"Doctor Name: {result[1]}")
        print(f"Hospital Id: {result[2]}")
        print(f"Joining Date: {result[3]}")
        print(f"Specialty: {result[4]}")
        print(f"Salary: {result[5]}")
        print(f"Experience: {result[6]}")
    else:
        print("No Doctor found with this ID.")

# Question 2: Read given hospital and doctor details
hospital_id = 2
doctor_id = 105

get_hospital_details(hospital_id)
get_doctor_details(doctor_id)

# Close connection
conn.close()


#C

def fetch_doctors_by_salary_specialty(min_salary, specialty):
    cursor.execute('''
    SELECT * FROM Doctor
    WHERE Salary > ? AND Speciality = ?
    ''', (min_salary, specialty))
    results = cursor.fetchall()
    
    if results:
        print(f"\nDoctors with salary more than {min_salary} and specialty '{specialty}':")
        for doctor in results:
            print(f"Doctor Id: {doctor[0]}, Name: {doctor[1]}, Salary: {doctor[5]}, Speciality: {doctor[4]}")
    else:
        print("\nNo doctor found with given salary and specialty.")

# Example
fetch_doctors_by_salary_specialty(25000, 'Pharmacologist')




#D

def update_doctor_experience(doctor_id, experience_years):
    cursor.execute('''
    UPDATE Doctor
    SET Experience = ?
    WHERE Doctor_Id = ?
    ''', (experience_years, doctor_id))
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"\nExperience updated for Doctor ID {doctor_id}.")
    else:
        print("\nNo doctor found with the given ID.")

# Example
update_doctor_experience(105, 12)



#E

def find_hospitals_with_more_than_50_doctors():
    cursor.execute('''
    SELECT Hospital.Hospital_Id, Hospital.Hospital_Name, COUNT(Doctor.Doctor_Id) as Doctor_Count
    FROM Hospital
    JOIN Doctor ON Hospital.Hospital_Id = Doctor.Hospital_Id
    GROUP BY Hospital.Hospital_Id
    HAVING Doctor_Count > 50
    ''')
    results = cursor.fetchall()
    
    if results:
        print("\nHospitals with more than 50 doctors:")
        for hospital in results:
            print(f"Hospital Id: {hospital[0]}, Name: {hospital[1]}, Number of Doctors: {hospital[2]}")
    else:
        print("\nNo hospital found with more than 50 doctors.")

# Example
find_hospitals_with_more_than_50_doctors()
"""

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)
