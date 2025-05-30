# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # مفتاح سري للتطبيق

# كلمة مرور المسؤول (يمكن تغييرها هنا)
ADMIN_PASSWORD = "admin123"

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

# إضافة موظف
def add_employee(name):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO employees (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# حذف موظف
def delete_employee(employee_id):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

# الحصول على جميع الموظفين
def get_all_employees():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    conn.close()
    return employees

# البحث عن موظف
def search_employee(name):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE name LIKE ?", ('%' + name + '%',))
    results = c.fetchall()
    conn.close()
    return results

# المسارات الرئيسية
@app.route('/')
def home():
    return redirect(url_for('gate_security'))

@app.route('/gate')
def gate_security():
    return render_template('gate_security.html')

@app.route('/admin')
def admin_dashboard():
    # التحقق من تسجيل الدخول
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employees = get_all_employees()
    return render_template('admin_dashboard.html', employees=employees)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # إذا كان مسجل دخول بالفعل، توجيه للوحة التحكم
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('كلمة المرور غير صحيحة!', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('تم تسجيل الخروج بنجاح!', 'success')
    return redirect(url_for('gate_security'))

@app.route('/add', methods=['POST'])
def add():
    # التحقق من تسجيل الدخول
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    name = request.form['name']
    if name.strip():
        if add_employee(name):
            flash('تمت إضافة الموظف بنجاح!', 'success')
        else:
            flash('هذا الموظف موجود بالفعل!', 'danger')
    else:
        flash('الرجاء إدخال اسم صحيح!', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:employee_id>')
def delete(employee_id):
    # التحقق من تسجيل الدخول
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    delete_employee(employee_id)
    flash('تم حذف الموظف بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/search', methods=['POST'])
def search():
    name = request.form['name']
    results = search_employee(name)
    return render_template('search_results.html', results=results, query=name)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)