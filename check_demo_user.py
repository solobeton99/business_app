import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

def check_demo_user():
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
            
            # Check if demo user exists
            cursor.execute("""
                SELECT id, name, email, password_hash 
                FROM users 
                WHERE email = %s
            """, ('demo@example.com',))
            
            user = cursor.fetchone()
            
            if user:
                print(f"Demo user found:")
                print(f"ID: {user['id']}")
                print(f"Name: {user['name']}")
                print(f"Email: {user['email']}")
                
                # Check if password matches
                test_password = 'demo123456'
                if check_password_hash(user['password_hash'], test_password):
                    print(f"Password '{test_password}' is correct!")
                else:
                    print(f"Password '{test_password}' is incorrect!")
                    
                # Try with another common password
                alt_password = 'demo'
                if check_password_hash(user['password_hash'], alt_password):
                    print(f"Password '{alt_password}' is correct!")
                else:
                    print(f"Password '{alt_password}' is incorrect!")
            else:
                print("Demo user not found!")
                
                # List all users in the database
                cursor.execute("SELECT id, name, email FROM users")
                users = cursor.fetchall()
                
                if users:
                    print("\nAll users in the database:")
                    for user in users:
                        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
                else:
                    print("No users found in the database!")
                
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    check_demo_user()
