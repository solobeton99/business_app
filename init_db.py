import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def init_database():
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host='sql.freedb.tech',
            port=3306,
            database='freedb_business_app',
            user='freedb_samego',
            password='J8SR@y%NHw?#F3v'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)

            # Create companies table
            create_companies_table = """
            CREATE TABLE IF NOT EXISTS companies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                address TEXT,
                phone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_companies_table)

            # Create user_companies table
            create_user_companies_table = """
            CREATE TABLE IF NOT EXISTS user_companies (
                user_id INT NOT NULL,
                company_id INT NOT NULL,
                role VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, company_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_user_companies_table)

            # Create clients table
            create_clients_table = """
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                contact_person VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                address TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_clients_table)

            # Create suppliers table
            create_suppliers_table = """
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                contact_person VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                address TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_suppliers_table)

            # Create income table
            create_income_table = """
            CREATE TABLE IF NOT EXISTS income (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description VARCHAR(255) NOT NULL,
                note TEXT,
                status ENUM('paid', 'unpaid', 'pending') DEFAULT 'paid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_income_table)

            # Create expenses table
            create_expenses_table = """
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description VARCHAR(255) NOT NULL,
                note TEXT,
                status ENUM('paid', 'unpaid', 'pending') DEFAULT 'paid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_expenses_table)

            # Create projects table
            create_projects_table = """
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                description TEXT,
                project_manager VARCHAR(255) NOT NULL,
                starting_date DATE NOT NULL,
                ending_date DATE,
                status ENUM('not started', 'ongoing', 'completed', 'cancelled') DEFAULT 'not started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_projects_table)

            # Create project notes table
            create_project_notes_table = """
            CREATE TABLE IF NOT EXISTS project_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                note_text TEXT NOT NULL,
                created_by INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_project_notes_table)

            # Create employees table
            create_employees_table = """
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                employee_name VARCHAR(255) NOT NULL,
                role VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50),
                status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
                salary DECIMAL(10, 2),
                starting_date DATE NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_employees_table)

            # Create invoices table
            create_invoices_table = """
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT NOT NULL,
                invoice_number VARCHAR(50) NOT NULL,
                invoice_type ENUM('Standard', 'Proforma', 'Quotation') DEFAULT 'Standard',
                client_id INT NOT NULL,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                status ENUM('Draft', 'Sent', 'Paid', 'Overdue') DEFAULT 'Draft',
                total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_invoices_table)

            # Create invoice_items table
            create_invoice_items_table = """
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_id INT NOT NULL,
                description TEXT NOT NULL,
                quantity DECIMAL(10, 2) NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                tax_rate DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_invoice_items_table)

            # Create demo user
            demo_email = 'demo@example.com'
            demo_password = 'demo'
            demo_name = 'demo'
            password_hash = generate_password_hash(demo_password)

            # Check if demo user already exists
            cursor.execute('SELECT id FROM users WHERE email = %s', (demo_email,))
            if not cursor.fetchone():
                insert_query = 'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)'
                cursor.execute(insert_query, (demo_name, demo_email, password_hash))
                connection.commit()
                print('Demo user created successfully!')
                # Create a demo company
                cursor.execute('SELECT id FROM companies WHERE company_name = %s', ('Demo Company',))
                demo_company = cursor.fetchone()
                if not demo_company:
                    cursor.execute('INSERT INTO companies (company_name, address, phone) VALUES (%s, %s, %s)',
                                 ('Demo Company', '123 Demo Street', '555-0100'))
                    company_id = cursor.lastrowid
                    cursor.execute('INSERT INTO user_companies (user_id, company_id, role) VALUES (%s, %s, %s)',
                                 (cursor.lastrowid, company_id, 'owner'))
                    
                    # Add demo suppliers
                    suppliers_data = [
                        ('Office Supplies Co.', 'John Smith', 'john@supplies.com', '555-0201', '456 Supply Ave'),
                        ('Tech Solutions Inc.', 'Jane Doe', 'jane@techsolutions.com', '555-0202', '789 Tech Blvd')
                    ]
                    for supplier in suppliers_data:
                        cursor.execute('INSERT INTO suppliers (company_id, name, contact_person, email, phone, address) '
                                     'VALUES (%s, %s, %s, %s, %s, %s)',
                                     (company_id, *supplier))
                    
                    # Add demo clients
                    clients_data = [
                        ('Retail Store LLC', 'Mike Johnson', 'mike@retail.com', '555-0301', '321 Store St'),
                        ('Restaurant Chain Co.', 'Sarah Wilson', 'sarah@restaurant.com', '555-0302', '654 Food Ave')
                    ]
                    for client in clients_data:
                        cursor.execute('INSERT INTO clients (company_id, name, contact_person, email, phone, address) '
                                     'VALUES (%s, %s, %s, %s, %s, %s)',
                                     (company_id, *client))
                    
                    # Add demo financial data (max 100 transactions)
                    from datetime import datetime, timedelta
                    import random

                    current_date = datetime.now()
                    transaction_count = 0
                    max_transactions = 100
                    days_back = 90  # Last 3 months

                    income_descriptions = ['Client Payment', 'Service Fee', 'Consulting', 'Project Milestone', 'Subscription']
                    expense_descriptions = ['Office Supplies', 'Utilities', 'Rent', 'Marketing', 'Equipment']
                    status_options = ['paid', 'unpaid', 'pending']

                    while transaction_count < max_transactions and days_back >= 0:
                        date = current_date - timedelta(days=days_back)
                        
                        # Add income entry
                        if transaction_count < max_transactions and random.random() < 0.5:
                            amount = random.uniform(1000, 5000)
                            cursor.execute('INSERT INTO income (company_id, amount, description, note, status, created_at) '
                                         'VALUES (%s, %s, %s, %s, %s, %s)',
                                         (company_id, amount, random.choice(income_descriptions),
                                          'Demo income entry', random.choices(status_options, weights=[0.8, 0.1, 0.1])[0],
                                          date))
                            transaction_count += 1

                        # Add expense entry
                        if transaction_count < max_transactions and random.random() < 0.5:
                            amount = random.uniform(500, 3000)
                            cursor.execute('INSERT INTO expenses (company_id, amount, description, note, status, created_at) '
                                         'VALUES (%s, %s, %s, %s, %s, %s)',
                                         (company_id, amount, random.choice(expense_descriptions),
                                          'Demo expense entry', random.choices(status_options, weights=[0.8, 0.1, 0.1])[0],
                                          date))
                            transaction_count += 1

                        days_back -= 1

                    connection.commit()
                    print('Demo data created successfully!')
            else:
                print('Demo user already exists')

            print('Database initialization completed successfully!')

    except Error as e:
        print(f'Error: {e}')

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print('Database connection closed.')

if __name__ == '__main__':
    init_database()