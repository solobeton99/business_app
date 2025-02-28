import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import mysql.connector
from mysql.connector import Error

def add_demo_financial_data():
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
            
            # Get demo user's companies
            cursor.execute('SELECT id FROM users WHERE email = %s', ('demo@sample.com',))
            user = cursor.fetchone()
            
            if user:
                # Get all companies for the user
                cursor.execute(
                    'SELECT c.id FROM companies c '
                    'JOIN user_companies uc ON c.id = uc.company_id '
                    'WHERE uc.user_id = %s',
                    (user['id'],)
                )
                companies = cursor.fetchall()
                
                if companies:
                    current_date = datetime.now()
                    
                    # Income and expense descriptions
                    income_descriptions = [
                        'Client Payment', 'Service Fee', 'Consulting',
                        'Project Milestone', 'Subscription', 'License Fee',
                        'Support Contract', 'Training Services', 'Custom Development',
                        'Maintenance Fee'
                    ]
                    
                    expense_descriptions = [
                        'Office Supplies', 'Utilities', 'Rent', 'Marketing',
                        'Equipment', 'Software Licenses', 'Employee Training',
                        'Travel Expenses', 'Insurance', 'Professional Services'
                    ]
                    
                    status_options = ['paid', 'unpaid', 'pending']
                    status_weights = [0.7, 0.2, 0.1]  # 70% paid, 20% unpaid, 10% pending
                    
                    for company in companies:
                        # Generate 90 days of transactions
                        for days_back in range(90, -1, -1):
                            date = current_date - timedelta(days=days_back)
                            
                            # Add income (60% chance)
                            if random.random() < 0.6:
                                amount = random.uniform(1000, 8000)
                                description = random.choice(income_descriptions)
                                status = random.choices(status_options, weights=status_weights)[0]
                                
                                cursor.execute(
                                    'INSERT INTO income (company_id, amount, description, note, status, created_at) '
                                    'VALUES (%s, %s, %s, %s, %s, %s)',
                                    (company['id'], round(amount, 2), description,
                                     f'Demo income entry - {description}', status, date)
                                )
                            
                            # Add expense (50% chance)
                            if random.random() < 0.5:
                                amount = random.uniform(500, 4000)
                                description = random.choice(expense_descriptions)
                                status = random.choices(status_options, weights=status_weights)[0]
                                
                                cursor.execute(
                                    'INSERT INTO expenses (company_id, amount, description, note, status, created_at) '
                                    'VALUES (%s, %s, %s, %s, %s, %s)',
                                    (company['id'], round(amount, 2), description,
                                     f'Demo expense entry - {description}', status, date)
                                )
                    
                    connection.commit()
                    print('Demo financial data added successfully!')
                else:
                    print('No companies found for demo user')
            else:
                print('Demo user not found')

    except Error as e:
        print(f'Error: {e}')

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print('Database connection closed.')

if __name__ == '__main__':
    add_demo_financial_data()