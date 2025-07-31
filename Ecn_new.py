from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

@app.route('/')
def index():
    if 'name' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect('ecn_coop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name = ? AND password = ? AND role = 'admin'", (name, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['name'] = name
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid admin credentials')
    return render_template('admin_login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect('ecn_coop.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, password, role) VALUES (?, ?, 'admin')", (name, password))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

@app.route('/dashboard')
def dashboard():
    if 'name' not in session:
        return redirect('/')
    role = session.get('role', 'staff')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    conn = sqlite3.connect('ecn_coop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM loan_applications WHERE user_id = (SELECT id FROM users WHERE name = ?)", (session['name'],))
    applications = c.fetchall()
    conn.close()
    return render_template('dashboard.html', applications=applications)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'name' not in session or session.get('role') != 'admin':
        return redirect('/admin_login')
    conn = sqlite3.connect('ecn_coop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    c.execute("SELECT * FROM loan_applications")
    applications = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users, applications=applications)

@app.route('/repayments')
def repayments():
    if 'name' not in session:
        return redirect('/')
    conn = sqlite3.connect('ecn_coop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM repayments WHERE user_id = (SELECT id FROM users WHERE name = ?)", (session['name'],))
    repayments = c.fetchall()
    conn.close()
    return render_template('repayments.html', repayments=repayments)

@app.route('/logout')
def logout():
    session.pop('name', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == '__main__':
    import sqlite3
    conn = sqlite3.connect('ecn_coop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT, role TEXT DEFAULT "staff")''')
    c.execute('''CREATE TABLE IF NOT EXISTS loan_applications (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS repayments (id INTEGER PRIMARY KEY, user_id INTEGER, due_date TEXT, amount REAL, status INTEGER)''')
    conn.commit()
    conn.close()
    app.run(debug=True)
