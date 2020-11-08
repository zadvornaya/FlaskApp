import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from testApp.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        dateOfBirth = request.form['dateOfBirth']
        db = get_db()
        error = None

        if not login:
            error = 'Необходимо ввести логин.'
        elif not password:
            error = 'Необходимо ввести пароль.'
        elif db.execute(
            'SELECT userID FROM Users WHERE login = ?', (login,)
        ).fetchone() is not None:
            error = 'Пользователь {} уже зарегистрирован.'.format(login)

        if error is None:
            db.execute(
                'INSERT INTO Users (login, password, name, surname, dateOfBirth) VALUES (?, ?, ?, ?, ?)',
                (login, generate_password_hash(password), name, surname, dateOfBirth)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Users WHERE login = ?', (login,)
        ).fetchone()

        if user is None:
            error = 'Неверный логин.'
        elif not check_password_hash(user['password'], password):
            error = 'Неверный пароль.'

        if error is None:
            session.clear()
            session['user_id'] = user['userID']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Users WHERE userID = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
