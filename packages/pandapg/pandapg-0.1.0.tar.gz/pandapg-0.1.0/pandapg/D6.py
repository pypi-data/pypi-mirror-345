code = """
# Q1 
import sqlite3

# 1. Connect to (or Create) the database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# 2. Create the EMP table
cursor.execute('''
CREATE TABLE IF NOT EXISTS EMP (
    Empid INTEGER PRIMARY KEY,
    Empname TEXT NOT NULL,
    Salary INTEGER NOT NULL CHECK (Salary > 5000),
    Commission FLOAT,
    Deptid INTEGER NOT NULL
)
''')

# 3. Commit and close
conn.commit()
print("Table EMP created successfully in DataAnalytics.db!")
conn.close()




#Q2

import sqlite3

# 1. Connect to the database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# 2. Delete records where Commission is NULL and Deptid not in (1, 2, 3)
cursor.execute('''
DELETE FROM EMP
WHERE Commission IS NULL
AND Deptid NOT IN (1, 2, 3)
''')

# 3. Commit and close
conn.commit()
print("Records deleted successfully where Commission is NULL and Deptid not in (D1, D2, D3).")
conn.close()



#Q3

import sqlite3

# Connect to database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Create DEPARTMENT table
cursor.execute('''
CREATE TABLE IF NOT EXISTS DEPARTMENT (
    Deptid INTEGER PRIMARY KEY,
    NumOfEmployees INTEGER,
    AvgSalary FLOAT
)
''')

conn.commit()
print("DEPARTMENT table created successfully!")
conn.close()




# Reconnect to database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Fetch average salary and count of employees per department
cursor.execute('''
SELECT Deptid, COUNT(*), AVG(Salary)
FROM EMP
GROUP BY Deptid
''')

departments = cursor.fetchall()

# Insert into DEPARTMENT table (only if AvgSalary > 12000)
for dept in departments:
    deptid, num_of_employees, avg_salary = dept
    if avg_salary >= 12000:
        cursor.execute('''
        INSERT INTO DEPARTMENT (Deptid, NumOfEmployees, AvgSalary)
        VALUES (?, ?, ?)
        ''', (deptid, num_of_employees, avg_salary))

conn.commit()
print("Inserted eligible departments into DEPARTMENT table!")
conn.close()




#Q4

import sqlite3

# Connect to database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Update salary of all employees by 5%
cursor.execute('''
UPDATE EMP
SET Salary = Salary * 1.05
''')

conn.commit()
print("All salaries updated by 5% successfully!")



# Fetch top 5 employees based on highest salary
cursor.execute('''
SELECT Empid, Empname, Salary
FROM EMP
ORDER BY Salary DESC
LIMIT 5
''')

top_5_employees = cursor.fetchall()

# Display the results
print("\nTop 5 Highest Paid Employees:")
for emp in top_5_employees:
    print(f"EmpID: {emp[0]}, Name: {emp[1]}, Salary: {emp[2]}")

conn.close()




#Q5

import sqlite3

# Connect to database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Step 1: Get current total salary before update
cursor.execute('SELECT SUM(Salary) FROM EMP')
total_salary_before = cursor.fetchone()[0]

# Step 2: Update salaries of John and Black
cursor.execute('''
UPDATE EMP
SET Salary = Salary + 2000
WHERE Empname = 'John'
''')

cursor.execute('''
UPDATE EMP
SET Salary = Salary + 5000
WHERE Empname = 'Black'
''')

# Step 3: Get the total salary after the update
cursor.execute('SELECT SUM(Salary) FROM EMP')
total_salary_after = cursor.fetchone()[0]

# Step 4: If total salary is greater than 50,000, undo the update
if total_salary_after > 50000:
    # Undo the updates by rolling back
    conn.rollback()
    print("Total salary exceeds 50,000, updates undone!")
else:
    conn.commit()
    print("Salaries of John and Black updated successfully!")

# Close the connection
conn.close()




#Q6

import sqlite3

# Connect to the database
conn = sqlite3.connect('DataAnalytics.db')
cursor = conn.cursor()

# Step 1: Accept employee ID and new salary
emp_id = int(input("Enter Employee ID to update salary: "))
new_salary = float(input(f"Enter new salary for Employee ID {emp_id}: "))

# Step 2: Check if the employee exists
cursor.execute('SELECT * FROM EMP WHERE Empid = ?', (emp_id,))
employee = cursor.fetchone()

if employee:
    # Employee exists, update the salary
    cursor.execute('''
    UPDATE EMP
    SET Salary = ?
    WHERE Empid = ?
    ''', (new_salary, emp_id))
    
    conn.commit()
    print(f"Salary for Employee ID {emp_id} updated successfully!")
else:
    # Employee doesn't exist
    print(f"Employee ID {emp_id} does not exist!")

# Close the connection
conn.close()

"""

def print_code():
    print(code)

if __name__ == "__main__":
    exec(code)
