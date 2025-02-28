import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

# Create demo user
conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor()
        email = 'demo@sample.com'
        password = 'demo123'
        name = 'Demo User'
        
        # Generate password hash
        password_hash = generate_password_hash(password)
        
        # Insert user
        cursor.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)',
            (name, email, password_hash)
        )
        conn.commit()
        print('Demo user created successfully!')
        print(f'Email: {email}')
        print(f'Password: {password}')
        
    except Error as e:
        print(f"Error creating demo user: {e}")
    finally:
        cursor.close()
        conn.close()