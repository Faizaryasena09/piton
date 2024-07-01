from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Gantilah dengan secret key yang aman
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Model untuk pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=False)  # Tambahkan kolom role

    def __repr__(self):
        return f'<User {self.username}>'

# Fungsi untuk membuat pengguna default
def create_default_users():
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='password', role='admin')
        db.session.add(admin_user)
    if not User.query.filter_by(username='user').first():
        regular_user = User(username='user', password='password', role='user')
        db.session.add(regular_user)
    db.session.commit()

# Buat database dan pengguna default
with app.app_context():
    db.create_all()
    create_default_users()

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = username
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('user_home'))
    return render_template('login.html', error=error)

# Halaman admin home
@app.route('/admin_home')
def admin_home():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_home.html')

# Halaman user home
@app.route('/user_home')
def user_home():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    return render_template('user_home.html')

# Halaman profile
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    return render_template('profile.html', user=user)

# Halaman change password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if user.password != current_password:
            error = 'Current password is incorrect.'
            return render_template('change_password.html', user=user, error=error)
        if new_password != confirm_password:
            error = 'New passwords do not match.'
            return render_template('change_password.html', user=user, error=error)
        user.password = new_password
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('change_password.html', user=user)

@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        new_username = request.form['new_username']
        if User.query.filter_by(username=new_username).first():
            error = 'Username already taken. Please choose a different one.'
            return render_template('change_username.html', error=error)
        
        user.username = new_username
        db.session.commit()
        session['username'] = new_username
        return redirect(url_for('profile'))
    
    return render_template('change_username.html')

# Halaman logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
