from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.config import mongo_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth', methods=['GET'])
def auth_page():
    return render_template('auth.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if not username or not email or not password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('auth.auth_page'))
    if mongo_db.users.find_one({'email': email}):
        flash('Email already registered.', 'danger')
        return redirect(url_for('auth.auth_page'))
    hashed_pw = generate_password_hash(password)
    mongo_db.users.insert_one({'username': username, 'email': email, 'password': hashed_pw})
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('auth.auth_page'))

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = mongo_db.users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.auth_page'))
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']
    flash('Logged in successfully.', 'success')
    return redirect(url_for('app_page'))  

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.auth_page'))
