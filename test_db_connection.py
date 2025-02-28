import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

def test_database_connection():
    try:
        # Test connection with a query that uses correct column names
        connection = mysql.connector.connect(
            host='sql.freedb.tech',
            port=3306,
            database='freedb_business_app',
            user='freedb_samego',
            password='J8SR@y%NHw?#F3v'
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL server version {db_info}")
            
            cursor = connection.cursor(dictionary=True)
            
            # Test companies table
            cursor.execute("SELECT company_name, address, phone FROM companies LIMIT 1;")
            company = cursor.fetchone()
            if company:
                print(f"Companies table: Found company '{company['company_name']}'")
            else:
                print("Companies table: Accessible but empty")
            
            # Test users table
            cursor.execute("SELECT email, password_hash FROM users LIMIT 1;")
            user = cursor.fetchone()
            if user:
                print(f"Users table: Found user with email '{user['email']}'")
            else:
                print("Users table: Accessible but empty")
            
            # Test clients table
            cursor.execute("SELECT name, contact_person, email FROM clients LIMIT 1;")
            client = cursor.fetchone()
            if client:
                print(f"Clients table: Found client '{client['name']}'")
            else:
                print("Clients table: Accessible but empty")
            
            # Test suppliers table
            cursor.execute("SELECT name, contact_person, email FROM suppliers LIMIT 1;")
            supplier = cursor.fetchone()
            if supplier:
                print(f"Suppliers table: Found supplier '{supplier['name']}'")
            else:
                print("Suppliers table: Accessible but empty")
            
            # Test employees table
            cursor.execute("SELECT employee_name, role, email FROM employees LIMIT 1;")
            employee = cursor.fetchone()
            if employee:
                print(f"Employees table: Found employee '{employee['employee_name']}'")
            else:
                print("Employees table: Accessible but empty")
            
            # Test projects table
            cursor.execute("SELECT project_name, project_manager, status FROM projects LIMIT 1;")
            project = cursor.fetchone()
            if project:
                print(f"Projects table: Found project '{project['project_name']}'")
            else:
                print("Projects table: Accessible but empty")
            
            # Test invoices table
            cursor.execute("SELECT invoice_number, invoice_type, status FROM invoices LIMIT 1;")
            invoice = cursor.fetchone()
            if invoice:
                print(f"Invoices table: Found invoice '{invoice['invoice_number']}'")
            else:
                print("Invoices table: Accessible but empty")
            
            return True

    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return False

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    test_database_connection()