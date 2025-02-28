import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import random

def add_mock_data_for_demo_user():
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
            cursor = connection.cursor(dictionary=True)
            
            # Get demo user ID
            cursor.execute("SELECT id FROM users WHERE email = 'demo@example.com'")
            user = cursor.fetchone()
            
            if not user:
                print("Demo user not found!")
                return
                
            user_id = user['id']
            print(f"Found demo user with ID: {user_id}")
            
            # Create mock companies
            company_names = [
                "TechInnovate Solutions", 
                "Global Marketing Group", 
                "Eco Friendly Products"
            ]
            
            company_ids = []
            
            for company_name in company_names:
                # Check if company already exists
                cursor.execute("SELECT id FROM companies WHERE company_name = %s", (company_name,))
                existing_company = cursor.fetchone()
                
                if existing_company:
                    company_id = existing_company['id']
                    print(f"Company '{company_name}' already exists with ID: {company_id}")
                else:
                    # Create new company
                    cursor.execute("""
                        INSERT INTO companies (company_name, address, phone) 
                        VALUES (%s, %s, %s)
                    """, (
                        company_name, 
                        f"{random.randint(1, 999)} Business Ave, Suite {random.randint(100, 999)}", 
                        f"+1 {random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    ))
                    company_id = cursor.lastrowid
                    print(f"Created company '{company_name}' with ID: {company_id}")
                
                # Link company to user if not already linked
                cursor.execute("""
                    SELECT * FROM user_companies 
                    WHERE user_id = %s AND company_id = %s
                """, (user_id, company_id))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO user_companies (user_id, company_id, role) 
                        VALUES (%s, %s, %s)
                    """, (user_id, company_id, "owner"))
                    print(f"Linked company '{company_name}' to demo user")
                
                company_ids.append(company_id)
            
            # Add clients for each company
            client_data = [
                ("Acme Corporation", "John Smith", "john@acme.com", "+1 555-123-4567", "123 Business St"),
                ("Globex Industries", "Jane Doe", "jane@globex.com", "+1 555-234-5678", "456 Industry Ave"),
                ("Stark Enterprises", "Tony Stark", "tony@stark.com", "+1 555-345-6789", "789 Innovation Blvd"),
                ("Wayne Enterprises", "Bruce Wayne", "bruce@wayne.com", "+1 555-456-7890", "101 Gotham St"),
                ("Umbrella Corporation", "Alice Johnson", "alice@umbrella.com", "+1 555-567-8901", "202 Research Dr")
            ]
            
            for company_id in company_ids:
                # Add 3-5 random clients per company
                num_clients = random.randint(3, 5)
                selected_clients = random.sample(client_data, num_clients)
                
                for client in selected_clients:
                    # Check if client already exists for this company
                    cursor.execute("""
                        SELECT id FROM clients 
                        WHERE company_id = %s AND name = %s
                    """, (company_id, client[0]))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO clients (company_id, name, contact_person, email, phone, address) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (company_id, *client))
                        print(f"Added client '{client[0]}' to company ID: {company_id}")
            
            # Add suppliers for each company
            supplier_data = [
                ("Office Supplies Inc.", "Mike Wilson", "mike@officesupplies.com", "+1 555-111-2222", "111 Supply St"),
                ("Tech Hardware Co.", "Sarah Brown", "sarah@techhardware.com", "+1 555-222-3333", "222 Hardware Ave"),
                ("Marketing Services Ltd.", "David Lee", "david@marketingservices.com", "+1 555-333-4444", "333 Marketing Blvd"),
                ("Logistics Partners", "Emma Davis", "emma@logisticspartners.com", "+1 555-444-5555", "444 Logistics Dr"),
                ("Consulting Experts", "Robert Johnson", "robert@consultingexperts.com", "+1 555-555-6666", "555 Consulting St")
            ]
            
            for company_id in company_ids:
                # Add 2-4 random suppliers per company
                num_suppliers = random.randint(2, 4)
                selected_suppliers = random.sample(supplier_data, num_suppliers)
                
                for supplier in selected_suppliers:
                    # Check if supplier already exists for this company
                    cursor.execute("""
                        SELECT id FROM suppliers 
                        WHERE company_id = %s AND name = %s
                    """, (company_id, supplier[0]))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO suppliers (company_id, name, contact_person, email, phone, address) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (company_id, *supplier))
                        print(f"Added supplier '{supplier[0]}' to company ID: {company_id}")
            
            # Add projects for each company
            project_names = [
                "Website Redesign", "Marketing Campaign", "Product Launch", 
                "Mobile App Development", "Brand Refresh", "Market Research",
                "Customer Satisfaction Survey", "Social Media Strategy", 
                "SEO Optimization", "Content Creation"
            ]
            
            project_managers = [
                "Michael Scott", "Jim Halpert", "Pam Beesly", 
                "Dwight Schrute", "Angela Martin", "Oscar Martinez"
            ]
            
            for company_id in company_ids:
                # Add 3-6 random projects per company
                num_projects = random.randint(3, 6)
                selected_projects = random.sample(project_names, num_projects)
                
                for project_name in selected_projects:
                    # Check if project already exists for this company
                    cursor.execute("""
                        SELECT id FROM projects 
                        WHERE company_id = %s AND project_name = %s
                    """, (company_id, project_name))
                    
                    if not cursor.fetchone():
                        # Random dates within the last year
                        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
                        end_date = start_date + timedelta(days=random.randint(30, 180))
                        
                        # Random status
                        status = random.choice(['not started', 'ongoing', 'completed', 'cancelled'])
                        
                        cursor.execute("""
                            INSERT INTO projects (company_id, project_name, description, project_manager, 
                                                starting_date, ending_date, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            company_id, 
                            project_name, 
                            f"This is a {project_name.lower()} project for the company.",
                            random.choice(project_managers),
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d'),
                            status
                        ))
                        print(f"Added project '{project_name}' to company ID: {company_id}")
            
            # Add financial data (income and expenses) for each company
            income_descriptions = [
                "Client Payment", "Service Fee", "Consulting", 
                "Project Milestone", "Subscription", "Product Sale"
            ]
            
            expense_descriptions = [
                "Office Supplies", "Utilities", "Rent", 
                "Marketing", "Equipment", "Software Subscription",
                "Employee Salary", "Travel Expenses", "Training"
            ]
            
            for company_id in company_ids:
                # Add 10-20 income entries per company
                num_income = random.randint(10, 20)
                
                for _ in range(num_income):
                    # Random date within the last year
                    date = datetime.now() - timedelta(days=random.randint(1, 365))
                    
                    # Random amount between $500 and $10,000
                    amount = round(random.uniform(500, 10000), 2)
                    
                    cursor.execute("""
                        INSERT INTO income (company_id, amount, description, note, status, created_at) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        company_id,
                        amount,
                        random.choice(income_descriptions),
                        "Mock income entry",
                        random.choices(['paid', 'unpaid', 'pending'], weights=[0.7, 0.2, 0.1])[0],
                        date.strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                print(f"Added {num_income} income entries to company ID: {company_id}")
                
                # Add 10-20 expense entries per company
                num_expenses = random.randint(10, 20)
                
                for _ in range(num_expenses):
                    # Random date within the last year
                    date = datetime.now() - timedelta(days=random.randint(1, 365))
                    
                    # Random amount between $100 and $5,000
                    amount = round(random.uniform(100, 5000), 2)
                    
                    cursor.execute("""
                        INSERT INTO expenses (company_id, amount, description, note, status, created_at) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        company_id,
                        amount,
                        random.choice(expense_descriptions),
                        "Mock expense entry",
                        random.choices(['paid', 'unpaid', 'pending'], weights=[0.7, 0.2, 0.1])[0],
                        date.strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                print(f"Added {num_expenses} expense entries to company ID: {company_id}")
            
            # Add employees for each company
            employee_roles = [
                "Manager", "Developer", "Designer", "Marketing Specialist", 
                "Sales Representative", "Customer Support", "HR Specialist",
                "Financial Analyst", "Project Manager", "Content Writer"
            ]
            
            employee_names = [
                "John Smith", "Jane Doe", "Michael Johnson", "Emily Williams",
                "David Brown", "Sarah Miller", "Robert Wilson", "Jennifer Moore",
                "William Taylor", "Elizabeth Anderson", "James Thomas", "Patricia Jackson",
                "Richard White", "Linda Harris", "Charles Martin", "Susan Thompson"
            ]
            
            for company_id in company_ids:
                # Add 5-10 employees per company
                num_employees = random.randint(5, 10)
                selected_employees = random.sample(employee_names, num_employees)
                
                for employee_name in selected_employees:
                    # Check if employee already exists for this company
                    cursor.execute("""
                        SELECT id FROM employees 
                        WHERE company_id = %s AND employee_name = %s
                    """, (company_id, employee_name))
                    
                    if not cursor.fetchone():
                        # Random start date within the last 5 years
                        start_date = datetime.now() - timedelta(days=random.randint(30, 1825))
                        
                        # Random salary between $30,000 and $120,000
                        salary = round(random.uniform(30000, 120000), 2)
                        
                        cursor.execute("""
                            INSERT INTO employees (company_id, employee_name, role, email, phone, status, salary, starting_date, note) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            company_id,
                            employee_name,
                            random.choice(employee_roles),
                            f"{employee_name.lower().replace(' ', '.')}@example.com",
                            f"+1 {random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                            random.choices(['active', 'inactive', 'suspended'], weights=[0.9, 0.08, 0.02])[0],
                            salary,
                            start_date.strftime('%Y-%m-%d'),
                            "Mock employee record"
                        ))
                        print(f"Added employee '{employee_name}' to company ID: {company_id}")
            
            # Add invoices for each company
            for company_id in company_ids:
                # Get clients for this company
                cursor.execute("SELECT id, name FROM clients WHERE company_id = %s", (company_id,))
                clients = cursor.fetchall()
                
                if not clients:
                    continue
                
                # Add 5-10 invoices per company
                num_invoices = random.randint(5, 10)
                
                for i in range(num_invoices):
                    # Random client
                    client = random.choice(clients)
                    
                    # Random dates within the last year
                    issue_date = datetime.now() - timedelta(days=random.randint(1, 365))
                    due_date = issue_date + timedelta(days=random.randint(15, 45))
                    
                    # Random invoice number
                    invoice_number = f"INV-{company_id}-{random.randint(1000, 9999)}"
                    
                    # Random status
                    status = random.choices(['Draft', 'Sent', 'Paid', 'Overdue'], weights=[0.2, 0.3, 0.4, 0.1])[0]
                    
                    # Random total amount
                    total_amount = round(random.uniform(500, 10000), 2)
                    
                    cursor.execute("""
                        INSERT INTO invoices (company_id, invoice_number, invoice_type, client_id, 
                                            issue_date, due_date, status, total_amount) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        company_id,
                        invoice_number,
                        random.choice(['Standard', 'Proforma', 'Quotation']),
                        client['id'],
                        issue_date.strftime('%Y-%m-%d'),
                        due_date.strftime('%Y-%m-%d'),
                        status,
                        total_amount
                    ))
                    
                    invoice_id = cursor.lastrowid
                    
                    # Add 1-5 items to each invoice
                    num_items = random.randint(1, 5)
                    
                    for _ in range(num_items):
                        # Random item details
                        description = random.choice([
                            "Consulting Services", "Web Development", "Design Work", 
                            "Marketing Services", "Product Purchase", "Support Hours",
                            "Training Session", "Software License", "Maintenance Fee"
                        ])
                        
                        quantity = round(random.uniform(1, 20), 2)
                        unit_price = round(random.uniform(50, 500), 2)
                        tax_rate = random.choice([0, 5, 7.5, 10, 15, 20])
                        
                        cursor.execute("""
                            INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, tax_rate) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            invoice_id,
                            description,
                            quantity,
                            unit_price,
                            tax_rate
                        ))
                    
                    print(f"Added invoice '{invoice_number}' with {num_items} items to company ID: {company_id}")
            
            connection.commit()
            print("\nMock data added successfully for demo user!")
            
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_mock_data_for_demo_user()
