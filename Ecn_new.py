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

#Admin login
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Admin Login - Energy Commission of Nigeria</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #f0f0f0;
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .header {
      background-color: #008000;
      color: white;
      padding: 10px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .header img {
      height: 50px;
      margin: 0 20px;
    }
    .login-container {
      background: rgba(255, 255, 255, 0.9);
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 400px;
    }
    .form-label { font-weight: bold; color: #333; }
    .btn-primary { background-color: #008000; border-color: #006400; }
    .btn-primary:hover { background-color: #006400; border-color: #004d00; }
    .error { color: #dc3545; font-size: 0.9em; margin-top: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <img src="{{ url_for('static', filename='images/ecn-logo.png') }}" alt="ECN Logo" class="ecn-logo">
    <h1>Energy Commission of Nigeria</h1>
    <img src="{{ url_for('static', filename='images/coat-of-arms.png') }}" alt="Nigerian Coat of Arms" class="coat-of-arms">
  </div>
  <div class="login-container">
    <h2 class="text-center mb-4">Admin Login</h2>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <form method="POST" action="/admin_login">
      <div class="mb-3">
        <label for="name" class="form-label">Admin Name</label>
        <input type="text" class="form-control" id="name" name="name" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
  </div>
</body>
</html>

#admin register
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Admin Register - Energy Commission of Nigeria</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f0f0f0; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .header { background-color: #008000; color: white; padding: 10px 0; display: flex; justify-content: space-between; align-items: center; }
    .header img { height: 50px; margin: 0 20px; }
    .login-container { background: rgba(255, 255, 255, 0.9); padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 100%; max-width: 400px; }
    .form-label { font-weight: bold; color: #333; }
    .btn-primary { background-color: #008000; border-color: #006400; }
    .btn-primary:hover { background-color: #006400; border-color: #004d00; }
    .error { color: #dc3545; font-size: 0.9em; margin-top: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <img src="{{ url_for('static', filename='images/ecn-logo.png') }}" alt="ECN Logo" class="ecn-logo">
    <h1>Energy Commission of Nigeria</h1>
    <img src="{{ url_for('static', filename='images/coat-of-arms.png') }}" alt="Nigerian Coat of Arms" class="coat-of-arms">
  </div>
  <div class="login-container">
    <h2 class="text-center mb-4">Admin Registration</h2>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <form method="POST" action="/admin_register">
      <div class="mb-3">
        <label for="name" class="form-label">Admin Name</label>
        <input type="text" class="form-control" id="name" name="name" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Register</button>
    </form>
    <a href="/admin_login" class="btn btn-outline-primary w-100 mt-3">Back to Login</a>
  </div>
</body>
</html>

#admin dashboard 
<!DOCTYPE html>
<html>
<head>
  <title>Admin Dashboard - Energy Commission of Nigeria</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f0f0f0; font-family: Arial, sans-serif; }
    .header { background-color: #008000; color: white; padding: 10px 0; text-align: center; }
    .header img { height: 50px; margin: 0 10px; }
    .container { max-width: 800px; margin-top: 20px; }
    table { background-color: white; }
  </style>
</head>
<body>
  <div class="header">
    <img src="{{ url_for('static', filename='images/ecn-logo.png') }}" alt="ECN Logo">
    <img src="{{ url_for('static', filename='images/coat-of-arms.png') }}" alt="Nigerian Coat of Arms">
    <h1>Energy Commission of Nigeria</h1>
  </div>
  <div class="container">
    <h2>Admin Dashboard</h2>
    <h3>Users</h3>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        {% for user in users %}
          <tr>
            <td>{{ user[0] }}</td>
            <td>{{ user[1] }}</td>
            <td>{{ user[3] }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
    <h3>Loan Applications</h3>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>User ID</th>
          <th>Amount (₦)</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {% for app in applications %}
          <tr>
            <td>{{ app[0] }}</td>
            <td>{{ app[1] }}</td>
            <td>{{ app[2] }}</td>
            <td>{{ app[3] }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
    <a href="/logout" class="btn btn-primary mt-3">Logout</a>
  </div>
</body>
</html>
