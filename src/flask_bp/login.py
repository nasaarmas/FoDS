from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src import db

login_bp = Blueprint('login', __name__, template_folder='src.templates')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.query(
            "SELECT login, haslo FROM Uzytkownik WHERE login = %s", (username,))

        if user and user[0][1] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dash.dashboard'))
        else:
            flash('This account doesn\'t exist.', 'info')

    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login.login'))