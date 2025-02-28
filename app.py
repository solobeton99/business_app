from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error, connect
from datetime import date
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = connect(
            host='sql.freedb.tech',
            port=3306,
            database='freedb_business_app',
            user='freedb_samego',
            password='J8SR@y%NHw?#F3v',
            autocommit=True
        )
        if not connection.is_connected():
            error_msg = "Failed to connect to database: Connection not established"
            print(error_msg)
            return None
        return connection
    except Error as e:
        error_msg = f"Error connecting to MySQL Database: {e}"
        print(error_msg)
        return None
    except Exception as e:
        error_msg = f"Unexpected error while connecting to database: {e}"
        print(error_msg)
        return None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Given a user_id, return the associated User object."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, email, password_hash 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['name'], user_data['email'])
        except Error as e:
            print(f"Error loading user: {e}")
        finally:
            cursor.close()
            conn.close()
    return None


class User(UserMixin):
    """Flask-Login user class."""
    def __init__(self, user_id, name, email):
        """
        :param user_id: int
        :param name: str
        :param email: str
        """
        self.id = user_id
        self.name = name
        self.email = email
        self.active_company = None
        self.locale = 'en'  # Default locale
        self.authenticated = True

    @staticmethod
    def get_by_email(email):
        """Fetch a User object by email."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id, name, email, password_hash 
                    FROM users 
                    WHERE email = %s
                """, (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data['id'], user_data['name'], user_data['email'])
            except Error as e:
                print(f"Error fetching user: {e}")
            finally:
                cursor.close()
                conn.close()
        return None


    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_active_company(self, company_id):
        self.active_company = company_id

    @staticmethod
    def get_by_email(email):
        """Fetch a User object by email."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id, name, email, password_hash 
                    FROM users 
                    WHERE email = %s
                """, (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data['id'], user_data['name'], user_data['email'])
            except Error as e:
                print(f"Error fetching user: {e}")
            finally:
                cursor.close()
                conn.close()
        return None


# -------------------- ROUTES -------------------- #

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Input validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        conn = get_db_connection()
        if not conn:
            flash('A database error occurred. Please try again later.', 'error')
            return render_template('register.html')

        try:
            cursor = conn.cursor(dictionary=True)
            # Check if user already exists
            cursor.execute("""
                SELECT id FROM users 
                WHERE email = %s
            """, (email,))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return render_template('register.html')

            # Create new user
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash) 
                VALUES (%s, %s, %s)
            """, (name, email, password_hash))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration', 'error')
            return render_template('register.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('A database error occurred. Please try again later.', 'error')
            return render_template('login.html')
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, email, password_hash 
                FROM users 
                WHERE email = %s
            """, (email,))
            user_data = cursor.fetchone()
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                user = User(user_data['id'], user_data['name'], user_data['email'])
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
        except Error as e:
            error_message = str(e)
            print(f"Database error during login: {error_message}")
            flash(f'Database error: {error_message}', 'error')
            return render_template('login.html')
        finally:
            if 'cursor' in locals():
                cursor.close()
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully')
    return redirect(url_for('login'))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/features-fr')
def features_fr():
    return render_template('features-fr.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission here
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        # Add your contact form processing logic here
        flash('Message sent successfully!')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/dashboard')
@app.route('/dashboard/<int:company_id>')
@login_required
def dashboard(company_id=None):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database')
        return render_template('dashboard.html', companies=[], active_company=None)

    try:
        cursor = conn.cursor(dictionary=True)
        # Get all companies for the dropdown
        cursor.execute("""
            SELECT id, company_name 
            FROM companies c
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
        """, (current_user.id,))
        companies = cursor.fetchall()
        
        # Get active company if company_id is provided
        active_company = None
        if company_id:
            cursor.execute("""
                SELECT id, company_name 
                FROM companies 
                WHERE id = %s AND id IN (
                    SELECT company_id FROM user_companies WHERE user_id = %s
                )
            """, (company_id, current_user.id))
            active_company = cursor.fetchone()
            if active_company:
                current_user.set_active_company(active_company['id'])

        # Fetch dashboard metrics if active company is selected
        metrics = {
            'total_revenue': 0,
            'active_projects': 0,
            'total_clients': 0,
            'pending_tasks': 0
        }

        if active_company:
            # Get total revenue
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM invoices
                WHERE company_id = %s AND status = 'paid'
            """, (active_company['id'],))
            result = cursor.fetchone()
            metrics['total_revenue'] = result['total'] if result else 0

            # Get active projects count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM projects
                WHERE company_id = %s AND status = 'active'
            """, (active_company['id'],))
            result = cursor.fetchone()
            metrics['active_projects'] = result['count'] if result else 0

            # Get total clients
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM clients
                WHERE company_id = %s
            """, (active_company['id'],))
            result = cursor.fetchone()
            metrics['total_clients'] = result['count'] if result else 0

            # Get pending tasks
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM tasks
                WHERE company_id = %s AND status = 'pending'
            """, (active_company['id'],))
            result = cursor.fetchone()
            metrics['pending_tasks'] = result['count'] if result else 0

        return render_template('dashboard.html', 
                             companies=companies, 
                             active_company=active_company,
                             metrics=metrics)
    except Error as e:
        print(f"Error fetching dashboard data: {e}")
        flash('An error occurred while loading the dashboard')
        return render_template('dashboard.html', companies=[], active_company=None)
    finally:
        cursor.close()
        conn.close()

@app.route('/my_companies')
@login_required
def my_companies():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.id, c.company_name, c.address, c.phone 
                FROM companies c
                JOIN user_companies uc ON c.id = uc.company_id
                WHERE uc.user_id = %s
            """, (current_user.id,))
            companies = cursor.fetchall()
            return render_template('my_companies.html', companies=companies)
        except Error as e:
            print(f"Error fetching companies: {e}")
            flash('An error occurred while fetching companies')
        finally:
            cursor.close()
            conn.close()
    return render_template('my_companies.html', companies=[])

@app.route('/add_company', methods=['GET', 'POST'])
@login_required
def add_company():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        address = request.form.get('address')
        phone = request.form.get('phone')

        if not company_name:
            flash('Company name is required')
            return render_template('add_company.html')

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # Insert company
                cursor.execute("""
                    INSERT INTO companies (company_name, address, phone) 
                    VALUES (%s, %s, %s)
                """, (company_name, address, phone))
                
                # Get the newly created company ID
                company_id = cursor.lastrowid
                
                # Create user-company relationship
                cursor.execute("""
                    INSERT INTO user_companies (user_id, company_id)
                    VALUES (%s, %s)
                """, (current_user.id, company_id))
                
                conn.commit()
                flash('Company added successfully!')
                return redirect(url_for('my_companies'))
            except Error as e:
                print(f"Error adding company: {e}")
                flash('An error occurred while adding the company')
            finally:
                cursor.close()
                conn.close()

    return render_template('add_company.html')

@app.route('/edit_company/<int:company_id>', methods=['GET', 'POST'])
@login_required
def edit_company(company_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('my_companies'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to edit it', 'error')
            return redirect(url_for('my_companies'))
        
        if request.method == 'POST':
            company_name = request.form.get('company_name')
            address = request.form.get('address')
            phone = request.form.get('phone')
            
            if not company_name:
                flash('Company name is required', 'error')
                return render_template('edit_company.html', company=company)
            
            cursor.execute("""
                UPDATE companies 
                SET company_name = %s, address = %s, phone = %s 
                WHERE id = %s
            """, (company_name, address, phone, company_id))
            conn.commit()
            flash('Company updated successfully!', 'success')
            return redirect(url_for('my_companies'))
        
        return render_template('edit_company.html', company=company)
    except Error as e:
        print(f"Error editing company: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('my_companies'))
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_company/<int:company_id>', methods=['POST'])
@login_required
def delete_company(company_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('my_companies'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to delete it', 'error')
            return redirect(url_for('my_companies'))
        
        # Delete user-company relationship first
        cursor.execute("""
            DELETE FROM user_companies 
            WHERE company_id = %s AND user_id = %s
        """, (company_id, current_user.id))
        
        # Then delete the company
        cursor.execute("""
            DELETE FROM companies 
            WHERE id = %s
        """, (company_id,))
        
        conn.commit()
        flash('Company deleted successfully!', 'success')
    except Error as e:
        print(f"Error deleting company: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('my_companies'))

@app.route('/suppliers')
@app.route('/suppliers/<int:company_id>')
@login_required
def suppliers(company_id=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Get all companies for the dropdown
            cursor.execute("""
                SELECT id, company_name 
                FROM companies c
                JOIN user_companies uc ON c.id = uc.company_id
                WHERE uc.user_id = %s
            """, (current_user.id,))
            companies = cursor.fetchall()
            
            # Get company details if company_id is provided
            company = None
            if company_id:
                cursor.execute("""
                    SELECT id, company_name 
                    FROM companies 
                    WHERE id = %s AND id IN (
                        SELECT company_id FROM user_companies WHERE user_id = %s
                    )
                """, (company_id, current_user.id))
                company = cursor.fetchone()
            
            # Get suppliers based on company_id
            if company_id:
                cursor.execute("""
                    SELECT s.*, comp.company_name 
                    FROM suppliers s 
                    JOIN companies comp ON s.company_id = comp.id 
                    WHERE s.company_id = %s
                """, (company_id,))
            else:
                cursor.execute("""
                    SELECT s.*, comp.company_name 
                    FROM suppliers s 
                    JOIN companies comp ON s.company_id = comp.id 
                    JOIN user_companies uc ON comp.id = uc.company_id 
                    WHERE uc.user_id = %s
                """, (current_user.id,))
            
            suppliers = cursor.fetchall()
            return render_template('suppliers.html', suppliers=suppliers, companies=companies, company=company)
        except Error as e:
            print(f"Error fetching suppliers: {e}")
            flash('An error occurred while fetching suppliers')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('suppliers.html', suppliers=[], companies=[], company=None)

@app.route('/add_supplier/<int:company_id>', methods=['GET', 'POST'])
@login_required
def add_supplier(company_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('suppliers'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to add suppliers to it', 'error')
            return redirect(url_for('suppliers'))
        
        if request.method == 'POST':
            name = request.form.get('name')
            contact_person = request.form.get('contact_person')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            if not name:
                flash('Supplier name is required', 'error')
                return render_template('add_supplier.html', company=company)
            
            cursor.execute("""
                INSERT INTO suppliers (company_id, name, contact_person, email, phone, address) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (company_id, name, contact_person, email, phone, address))
            conn.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('suppliers', company_id=company_id))
        
        return render_template('add_supplier.html', company=company)
    except Error as e:
        print(f"Error adding supplier: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('suppliers'))
    finally:
        cursor.close()
        conn.close()

@app.route('/edit_supplier/<int:company_id>/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(company_id, supplier_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('suppliers'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to edit its suppliers', 'error')
            return redirect(url_for('suppliers'))
        
        # Get supplier details
        cursor.execute("""
            SELECT * FROM suppliers WHERE id = %s AND company_id = %s
        """, (supplier_id, company_id))
        supplier = cursor.fetchone()
        
        if not supplier:
            flash('Supplier not found or does not belong to the selected company', 'error')
            return redirect(url_for('suppliers', company_id=company_id))
        
        if request.method == 'POST':
            name = request.form.get('name')
            contact_person = request.form.get('contact_person')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            if not name:
                flash('Supplier name is required', 'error')
                return render_template('edit_supplier.html', company=company, supplier=supplier)
            
            cursor.execute("""
                UPDATE suppliers 
                SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s 
                WHERE id = %s AND company_id = %s
            """, (name, contact_person, email, phone, address, supplier_id, company_id))
            conn.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('suppliers', company_id=company_id))
        
        return render_template('edit_supplier.html', company=company, supplier=supplier)
    except Error as e:
        print(f"Error editing supplier: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('suppliers'))
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_supplier/<int:company_id>/<int:supplier_id>')
@login_required
def delete_supplier(company_id, supplier_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('suppliers'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to delete its suppliers', 'error')
            return redirect(url_for('suppliers'))
        
        # Delete supplier
        cursor.execute("""
            DELETE FROM suppliers WHERE id = %s AND company_id = %s
        """, (supplier_id, company_id))
        conn.commit()
        flash('Supplier deleted successfully!', 'success')
    except Error as e:
        print(f"Error deleting supplier: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('suppliers', company_id=company_id))

@app.route('/projects')
@login_required
def projects():
    return render_template('projects_standalone.html')

@app.route('/manage_employees/<int:company_id>')
@login_required
def manage_employees(company_id):
    return render_template('employees_standalone.html')

@app.route('/income')
@login_required
def income():
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return render_template('income_standalone.html', income_entries=[], income_data={'labels': [], 'values': []})
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all companies for the user
        cursor.execute("""
            SELECT c.id, c.company_name 
            FROM companies c
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
        """, (current_user.id,))
        user_companies = cursor.fetchall()
        
        # Get income entries for all user's companies
        cursor.execute("""
            SELECT i.*, c.company_name 
            FROM income i
            JOIN companies c ON i.company_id = c.id
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
            ORDER BY i.created_at DESC
        """, (current_user.id,))
        income_entries = cursor.fetchall()
        
        # Prepare data for chart
        # Get monthly income for the last 6 months
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(amount) as total
            FROM income
            WHERE company_id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
            AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month
        """, (current_user.id,))
        monthly_income = cursor.fetchall()
        
        # Format data for Chart.js
        labels = []
        values = []
        for month in monthly_income:
            labels.append(month['month'])
            values.append(float(month['total']))
        
        income_data = {
            'labels': labels,
            'values': values
        }
        
        return render_template('income_standalone.html', 
                             income_entries=income_entries, 
                             user_companies=user_companies,
                             income_data=income_data)
    except Error as e:
        print(f"Error fetching income data: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('income_standalone.html', income_entries=[], income_data={'labels': [], 'values': []})
    finally:
        cursor.close()
        conn.close()

@app.route('/expenses')
@login_required
def expenses():
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return render_template('expenses_standalone.html', expense_entries=[], expense_data={'labels': [], 'values': []})
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all companies for the user
        cursor.execute("""
            SELECT c.id, c.company_name 
            FROM companies c
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
        """, (current_user.id,))
        user_companies = cursor.fetchall()
        
        # Get expense entries for all user's companies
        cursor.execute("""
            SELECT e.*, c.company_name 
            FROM expenses e
            JOIN companies c ON e.company_id = c.id
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
            ORDER BY e.created_at DESC
        """, (current_user.id,))
        expense_entries = cursor.fetchall()
        
        # Prepare data for chart
        # Get monthly expenses for the last 6 months
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(amount) as total
            FROM expenses
            WHERE company_id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
            AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month
        """, (current_user.id,))
        monthly_expenses = cursor.fetchall()
        
        # Format data for Chart.js
        labels = []
        values = []
        for month in monthly_expenses:
            labels.append(month['month'])
            values.append(float(month['total']))
        
        expense_data = {
            'labels': labels,
            'values': values
        }
        
        return render_template('expenses_standalone.html', 
                             expense_entries=expense_entries, 
                             user_companies=user_companies,
                             expense_data=expense_data)
    except Error as e:
        print(f"Error fetching expense data: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('expenses_standalone.html', expense_entries=[], expense_data={'labels': [], 'values': []})
    finally:
        cursor.close()
        conn.close()

@app.route('/invoices')
@login_required
def invoices():
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return render_template('invoices_standalone.html', invoices=[], clients=[])
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all invoices for the user's companies
        cursor.execute("""
            SELECT i.*, c.name as client_name
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN companies comp ON i.company_id = comp.id
            JOIN user_companies uc ON comp.id = uc.company_id
            WHERE uc.user_id = %s
            ORDER BY i.issue_date DESC
        """, (current_user.id,))
        invoices = cursor.fetchall()
        
        # Get all clients for the invoice creation form
        cursor.execute("""
            SELECT c.*
            FROM clients c
            JOIN companies comp ON c.company_id = comp.id
            JOIN user_companies uc ON comp.id = uc.company_id
            WHERE uc.user_id = %s
        """, (current_user.id,))
        clients = cursor.fetchall()
        
        return render_template('invoices_standalone.html', invoices=invoices, clients=clients)
    except Error as e:
        print(f"Error fetching invoices: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('invoices_standalone.html', invoices=[], clients=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/create_invoice', methods=['POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        issue_date = request.form.get('issue_date')
        due_date = request.form.get('due_date')
        invoice_type = request.form.get('invoice_type', 'Standard')
        
        # Get descriptions, quantities, unit prices, and tax rates
        descriptions = request.form.getlist('descriptions[]')
        quantities = request.form.getlist('quantities[]')
        unit_prices = request.form.getlist('unit_prices[]')
        tax_rates = request.form.getlist('tax_rates[]')
        
        if not client_id or not issue_date or not due_date:
            flash('Missing required fields', 'error')
            return redirect(url_for('invoices'))
        
        conn = get_db_connection()
        if not conn:
            flash('Unable to connect to database', 'error')
            return redirect(url_for('invoices'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get client's company_id
            cursor.execute("SELECT company_id FROM clients WHERE id = %s", (client_id,))
            client = cursor.fetchone()
            if not client:
                flash('Client not found', 'error')
                return redirect(url_for('invoices'))
            
            company_id = client['company_id']
            
            # Generate invoice number
            cursor.execute("""
                SELECT COUNT(*) as count FROM invoices WHERE company_id = %s
            """, (company_id,))
            count = cursor.fetchone()['count']
            invoice_number = f"INV-{company_id}-{count+1:04d}"
            
            # Calculate total amount
            total_amount = 0
            for i in range(len(descriptions)):
                if i < len(quantities) and i < len(unit_prices) and i < len(tax_rates):
                    qty = float(quantities[i])
                    price = float(unit_prices[i])
                    tax = float(tax_rates[i]) / 100
                    item_total = qty * price * (1 + tax)
                    total_amount += item_total
            
            # Insert invoice
            cursor.execute("""
                INSERT INTO invoices (invoice_number, company_id, client_id, issue_date, due_date, total_amount, status, invoice_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (invoice_number, company_id, client_id, issue_date, due_date, total_amount, 'Draft', invoice_type))
            
            invoice_id = cursor.lastrowid
            
            # Insert invoice items
            for i in range(len(descriptions)):
                if i < len(quantities) and i < len(unit_prices) and i < len(tax_rates):
                    description = descriptions[i]
                    quantity = float(quantities[i])
                    unit_price = float(unit_prices[i])
                    tax_rate = float(tax_rates[i])
                    
                    cursor.execute("""
                        INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, tax_rate)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (invoice_id, description, quantity, unit_price, tax_rate))
            
            conn.commit()
            flash('Invoice created successfully!', 'success')
        except Error as e:
            print(f"Error creating invoice: {e}")
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('invoices'))

@app.route('/view_invoice/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('invoices'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get invoice details
        cursor.execute("""
            SELECT i.*, c.name as client_name, c.email as client_email, c.address as client_address,
                   comp.company_name, comp.address as company_address, comp.phone as company_phone
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN companies comp ON i.company_id = comp.id
            JOIN user_companies uc ON comp.id = uc.company_id
            WHERE i.id = %s AND uc.user_id = %s
        """, (invoice_id, current_user.id))
        invoice = cursor.fetchone()
        
        if not invoice:
            flash('Invoice not found or you do not have permission to view it', 'error')
            return redirect(url_for('invoices'))
        
        # Get invoice items
        cursor.execute("""
            SELECT * FROM invoice_items WHERE invoice_id = %s
        """, (invoice_id,))
        items = cursor.fetchall()
        
        return render_template('view_invoice.html', invoice=invoice, items=items)
    except Error as e:
        print(f"Error viewing invoice: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('invoices'))
    finally:
        cursor.close()
        conn.close()

@app.route('/download_invoice_pdf/<int:invoice_id>')
@login_required
def download_invoice_pdf(invoice_id):
    # This would normally generate a PDF, but for now we'll just redirect back
    flash('PDF download functionality will be implemented soon', 'info')
    return redirect(url_for('view_invoice', invoice_id=invoice_id))

@app.route('/my_tasks')
@app.route('/my-tasks')
@login_required
def my_tasks():
    return render_template('my_tasks_standalone.html')

@app.route('/data-analysis')
@login_required
def data_analysis():
    return render_template('data_analysis_standalone.html')

@app.route('/stocks')
@login_required
def stocks():
    return render_template('stocks_standalone.html')

@app.route('/marketplace')
@login_required
def marketplace():
    return render_template('marketplace_standalone.html')

@app.route('/clients')
@app.route('/clients/<int:company_id>')
@login_required
def clients(company_id=None):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database')
        return render_template('clients.html', clients=[], companies=[], company=None)

    try:
        cursor = conn.cursor(dictionary=True)
        # Get all companies for the dropdown
        cursor.execute("""
            SELECT id, company_name 
            FROM companies c
            JOIN user_companies uc ON c.id = uc.company_id
            WHERE uc.user_id = %s
        """, (current_user.id,))
        companies = cursor.fetchall()

        # Get active company if company_id is provided
        company = None
        clients = []
        if company_id:
            cursor.execute("""
                SELECT * FROM companies 
                WHERE id = %s AND id IN (
                    SELECT company_id FROM user_companies WHERE user_id = %s
                )
            """, (company_id, current_user.id))
            company = cursor.fetchone()
            
            if company:
                cursor.execute("""
                    SELECT * FROM clients 
                    WHERE company_id = %s
                """, (company_id,))
                clients = cursor.fetchall()

        return render_template('clients.html', clients=clients, companies=companies, company=company)
    except Error as e:
        print(f"Error fetching clients: {e}")
        flash('An error occurred while fetching clients')
        return render_template('clients.html', clients=[], companies=[], company=None)
    finally:
        cursor.close()
        conn.close()

@app.route('/add_client/<int:company_id>', methods=['GET', 'POST'])
@login_required
def add_client(company_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('clients'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to add clients to it', 'error')
            return redirect(url_for('clients'))
        
        if request.method == 'POST':
            name = request.form.get('name')
            contact_person = request.form.get('contact_person')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            if not name:
                flash('Client name is required', 'error')
                return render_template('add_client.html', company=company)
            
            cursor.execute("""
                INSERT INTO clients (company_id, name, contact_person, email, phone, address) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (company_id, name, contact_person, email, phone, address))
            conn.commit()
            flash('Client added successfully!', 'success')
            return redirect(url_for('clients', company_id=company_id))
        
        return render_template('add_client.html', company=company)
    except Error as e:
        print(f"Error adding client: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('clients'))
    finally:
        cursor.close()
        conn.close()

@app.route('/edit_client/<int:company_id>/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(company_id, client_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('clients'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to edit its clients', 'error')
            return redirect(url_for('clients'))
        
        # Get client details
        cursor.execute("""
            SELECT * FROM clients WHERE id = %s AND company_id = %s
        """, (client_id, company_id))
        client = cursor.fetchone()
        
        if not client:
            flash('Client not found or does not belong to the selected company', 'error')
            return redirect(url_for('clients', company_id=company_id))
        
        if request.method == 'POST':
            name = request.form.get('name')
            contact_person = request.form.get('contact_person')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            if not name:
                flash('Client name is required', 'error')
                return render_template('edit_client.html', company=company, client=client)
            
            cursor.execute("""
                UPDATE clients 
                SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s 
                WHERE id = %s AND company_id = %s
            """, (name, contact_person, email, phone, address, client_id, company_id))
            conn.commit()
            flash('Client updated successfully!', 'success')
            return redirect(url_for('clients', company_id=company_id))
        
        return render_template('edit_client.html', company=company, client=client)
    except Error as e:
        print(f"Error editing client: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('clients'))
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_client/<int:company_id>/<int:client_id>')
@login_required
def delete_client(company_id, client_id):
    conn = get_db_connection()
    if not conn:
        flash('Unable to connect to database', 'error')
        return redirect(url_for('clients'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Check if company exists and belongs to user
        cursor.execute("""
            SELECT * FROM companies 
            WHERE id = %s AND id IN (
                SELECT company_id FROM user_companies WHERE user_id = %s
            )
        """, (company_id, current_user.id))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found or you do not have permission to delete its clients', 'error')
            return redirect(url_for('clients'))
        
        # Delete client
        cursor.execute("""
            DELETE FROM clients WHERE id = %s AND company_id = %s
        """, (client_id, company_id))
        conn.commit()
        flash('Client deleted successfully!', 'success')
    except Error as e:
        print(f"Error deleting client: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('clients', company_id=company_id))
