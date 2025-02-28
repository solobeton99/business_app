import os
from dotenv import load_dotenv
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash

load_dotenv()

def create_demo_user():
    try:
        connection = connect(
            host='sql.freedb.tech',
            port=3306,
            database='freedb_business_app',
            user='freedb_samego',
            password='J8SR@y%NHw?#F3v'
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check if demo user already exists
            cursor.execute('SELECT id FROM users WHERE email = %s', ('demo@example.com',))
            if cursor.fetchone():
                print('Demo user already exists!')
                return

            # Create demo user
            password_hash = generate_password_hash('demo123456')
            cursor.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)',
                ('Demo User', 'demo@example.com', password_hash)
            )
            connection.commit()
            print('Demo user created successfully!')

    except Error as e:
        print(f'Error creating demo user: {e}')
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    create_demo_user()