import mysql.connector
from mysql.connector import Error

def add_name_column():
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
            
            # Check if name column exists
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'freedb_business_app' 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'name'
            """)
            
            if not cursor.fetchone():
                print("'name' column does not exist in users table. Adding it now...")
                
                # Add name column to users table
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN name VARCHAR(255) NOT NULL DEFAULT 'User'
                """)
                
                # Update existing users with a default name based on their email
                cursor.execute("""
                    UPDATE users 
                    SET name = CONCAT('User ', SUBSTRING_INDEX(email, '@', 1))
                """)
                
                connection.commit()
                print("'name' column added successfully and existing users updated!")
            else:
                print("'name' column already exists in users table.")
                
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    add_name_column()
