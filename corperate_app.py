import sqlite3
from datetime import datetime
# Step 2: Create Employee class to handle employee data
class Employee:
    def _init_(self, emp_id, name, department, position, salary, hire_date):
        self.emp_id = emp_id
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary
        self.hire_date = hire_date

    def display_info(self):
        return f"ID: {self.emp_id}\nName: {self.name}\nDept: {self.department}\nPosition: {self.position}\nSalary: ${self.salary}"
# Step 3: Create Database Manager class to handle database operations
class DatabaseManager:
    def _init_(self):
        self.conn = sqlite3.connect('employee_db.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY,
                name TEXT,
                department TEXT,
                position TEXT,
                salary REAL,
                hire_date TEXT
            )
        ''')
        self.conn.commit()

    def add_employee(self, employee):
        self.cursor.execute('''
            INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)
        ''', (employee.emp_id, employee.name, employee.department,
              employee.position, employee.salary, employee.hire_date))
        self.conn.commit()
    def get_employee(self, emp_id):
        self.cursor.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,))
        return self.cursor.fetchone()

    def _del_(self):
        self.conn.close()
# Step 4: Create CorporateApplication class as the main application
class CorporateApplication:
    def _init_(self):
        self.db = DatabaseManager()
        self.logged_in = False

    def login(self, username, password):
        # Simple authentication (in real app, use proper security)
        if username == "admin" and password == "admin123":
            self.logged_in = True
            return "Login successful"
        return "Login failed"

    def add_new_employee(self, emp_id, name, dept, position, salary):
        if not self.logged_in:
            return "Please login first"

        hire_date = datetime.now().strftime("%Y-%m-%d")
        new_employee = Employee(emp_id, name, dept, position, salary, hire_date)
        self.db.add_employee(new_employee)
        return f"Employee {name} added successfully"

    def view_employee(self, emp_id):
        if not self.logged_in:
            return "Please login first"
        employee_data = self.db.get_employee(emp_id)
        if employee_data:
          return f"Employee Found:\nID: {employee_data[0]}\nName: {employee_data[1]}\nDept: {employee_data[2]}\nPosition: {employee_data[3]}\nSalary: ${employee_data[4]}\nHire Date: {employee_data[5]}"
        return "Employee not found"
# Step 5: Main execution function
def main():
    app = CorporateApplication()

    # Example usage
    print(app.login("admin", "admin123"))

    # Add a new employee
    print(app.add_new_employee(
        "EMP001",
        "John Doe",
        "IT",
        "Developer",
        75000
    ))

    # View employee details
    print(app.view_employee("EMP001"))

