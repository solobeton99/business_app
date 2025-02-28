import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import os

# Load environment variables
load_dotenv()

def create_demo_data():
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Create demo user
            demo_email = 'demo@sample.com'
            demo_password = 'demo123'
            demo_name = 'Demo User'
            password_hash = generate_password_hash(demo_password)

            # Check if demo user already exists
            cursor.execute('SELECT id FROM users WHERE email = %s', (demo_email,))
            user = cursor.fetchone()
            
            if not user:
                # Create user
                cursor.execute(
                    'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)',
                    (demo_name, demo_email, password_hash)
                )
                user_id = cursor.lastrowid
                print(f'Demo user created successfully with ID: {user_id}')
            else:
                user_id = user['id']
                print(f'Using existing user with ID: {user_id}')

            # Create demo companies
            companies_data = [
                ('Tech Innovators Ltd', '789 Innovation Way', '555-0123'),
                ('Creative Solutions Inc', '456 Design Street', '555-0124'),
                ('Global Services Corp', '321 Service Avenue', '555-0125')
            ]

            for company_data in companies_data:
                cursor.execute(
                    'INSERT INTO companies (company_name, address, phone) VALUES (%s, %s, %s)',
                    company_data
                )
                company_id = cursor.lastrowid
                
                # Link company to user
                cursor.execute(
                    'INSERT INTO user_companies (user_id, company_id, role) VALUES (%s, %s, %s)',
                    (user_id, company_id, 'owner')
                )

                # Add clients for each company
                clients_data = [
                    (company_id, f'Client A - {company_data[0]}', 'John Contact', f'john@client-a-{company_id}.com', '555-1001', '123 Client Street', 'Premium client'),
                    (company_id, f'Client B - {company_data[0]}', 'Jane Manager', f'jane@client-b-{company_id}.com', '555-1002', '456 Client Avenue', 'Regular client'),
                    (company_id, f'Client C - {company_data[0]}', 'Bob Executive', f'bob@client-c-{company_id}.com', '555-1003', '789 Client Road', 'New client')
                ]
                
                for client in clients_data:
                    cursor.execute(
                        'INSERT INTO clients (company_id, name, contact_person, email, phone, address, note) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        client
                    )

                # Add suppliers for each company
                suppliers_data = [
                    (company_id, 'Office Supplies Co', 'Mark Supplier', 'mark@supplies.com', '555-2001', '123 Supply St', 'Office materials'),
                    (company_id, 'Tech Hardware Ltd', 'Lisa Vendor', 'lisa@techhw.com', '555-2002', '456 Hardware Ave', 'Hardware supplier'),
                    (company_id, 'Marketing Agency', 'Tom Marketing', 'tom@marketing.com', '555-2003', '789 Agency Blvd', 'Marketing services')
                ]

                for supplier in suppliers_data:
                    cursor.execute(
                        'INSERT INTO suppliers (company_id, name, contact_person, email, phone, address, note) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        supplier
                    )

                # Add employees for each company
                employees_data = [
                    (company_id, 'Alice Johnson', 'Project Manager', 'alice@company.com', '555-3001', 'active', 75000, datetime.now().date(), 'Senior PM'),
                    (company_id, 'Bob Smith', 'Developer', 'bob@company.com', '555-3002', 'active', 65000, datetime.now().date(), 'Full-stack developer'),
                    (company_id, 'Carol White', 'Designer', 'carol@company.com', '555-3003', 'active', 60000, datetime.now().date(), 'UI/UX specialist')
                ]

                for employee in employees_data:
                    cursor.execute(
                        'INSERT INTO employees (company_id, employee_name, role, email, phone, status, salary, starting_date, note) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        employee
                    )

                # Add projects for each company
                projects_data = [
                    (company_id, 'Website Redesign', 'Complete overhaul of company website', 'Sarah Project', datetime.now().date(), datetime.now().date() + timedelta(days=30), 'ongoing'),
                    (company_id, 'Mobile App Development', 'New mobile application development', 'Mike Tech', datetime.now().date(), datetime.now().date() + timedelta(days=60), 'not started'),
                    (company_id, 'Cloud Migration', 'Migrate infrastructure to cloud', 'John Cloud', datetime.now().date(), datetime.now().date() + timedelta(days=45), 'ongoing')
                ]
                
                for project in projects_data:
                    cursor.execute(
                        'INSERT INTO projects (company_id, project_name, description, project_manager, starting_date, ending_date, status) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        project
                    )

                # Add invoices and invoice items
                for client_index, client_data in enumerate(clients_data):
                    cursor.execute('SELECT id FROM clients WHERE email = %s', (client_data[3],))
                    client_id = cursor.fetchone()['id']
                    
                    invoice_data = (
                        company_id,
                        f'INV-{company_id}-{client_id}-{datetime.now().strftime("%Y%m%d")}',
                        'Standard',
                        client_id,
                        datetime.now().date(),
                        datetime.now().date() + timedelta(days=30),
                        random.choice(['Draft', 'Sent', 'Paid'])
                    )

                    cursor.execute(
                        'INSERT INTO invoices (company_id, invoice_number, invoice_type, client_id, issue_date, due_date, status) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        invoice_data
                    )
                    invoice_id = cursor.lastrowid

                    # Add invoice items
                    items_data = [
                        ('Professional Services', 10, 150.00, 10.00),
                        ('Consulting Hours', 20, 200.00, 10.00),
                        ('Software License', 1, 1000.00, 10.00)
                    ]

                    for item in items_data:
                        cursor.execute(
                            'INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, tax_rate) '
                            'VALUES (%s, %s, %s, %s, %s)',
                            (invoice_id, *item)
                        )

            connection.commit()
            print('Demo data created successfully!')
            print(f'Login credentials:\nEmail: {demo_email}\nPassword: {demo_password}')

    except Error as e:
        print(f'Error: {e}')

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print('Database connection closed.')

if __name__ == '__main__':
    create_demo_data()