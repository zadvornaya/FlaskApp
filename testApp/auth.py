import functools

from flask import Blueprint, g, redirect, render_template, session, url_for
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import InputRequired, Regexp, Length, Optional, ValidationError

from testApp.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def validateLogup(form, field):
    db = get_db()
    if db.execute(
            'SELECT userID FROM Users WHERE login = ?', (field.data,)
    ).fetchone() is not None:
        raise ValidationError('Пользователь {} уже зарегистрирован.'.format(field.data))


class LogUpForm(FlaskForm):
    login = StringField('Логин*', validators=[InputRequired(message="Необходимо ввести логин."),
                                              Length(min=4, max=15,
                                                     message="Логин должен содержать от 4 до 15 символов."),
                                              validateLogup])
    password = PasswordField('Пароль*',
                             validators=[InputRequired(message="Необходимо ввести пароль."),
                                         Length(min=8, message="Пароль должен содержать минимум 8 символов."),
                                         Regexp("(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])",
                                                message="Пароль должен содержать хотя бы одно число, спецсимвол, "
                                                        "латинскую букву в нижнем и верхнем регистре.")])
    surname = StringField('Фамилия', validators=[Optional(), Regexp("^.*[A-zА-яЁё].*$",
                                                                    message="Фамилия должна содержать только буквы.")])
    name = StringField('Имя', validators=[Optional(), Regexp("^.*[A-zА-яЁё].*$",
                                                             message="Фамилия должна содержать только буквы.")])
    patronym = StringField('Отчество', validators=[Optional(), Regexp("^.*[A-zА-яЁё].*$",
                                                                      message="Фамилия должна содержать только буквы.")])
    dateOfBirth = DateField('Дата рождения', validators=[Optional()], format='%d.%m.%Y')
    submit = SubmitField('Зарегистрироваться')


def validateLogin(form, field):
    db = get_db()
    user = db.execute(
        'SELECT * FROM Users WHERE login = ?', (field.data,)
    ).fetchone()
    if user is None:
        raise ValidationError('Неверный логин.')


def validatePassword(form, field):
    db = get_db()
    user = db.execute(
        'SELECT * FROM Users WHERE login = ?', (form.login.data,)
    ).fetchone()
    if user is not None and not check_password_hash(user['password'], field.data):
        raise ValidationError('Неверный пароль.')


class LogInForm(FlaskForm):
    login = StringField('Логин*', validators=[InputRequired(message="Необходимо ввести логин."), validateLogin])
    password = PasswordField('Пароль*', validators=[InputRequired(message="Необходимо ввести пароль."),
                                                    validatePassword])
    submit = SubmitField('Войти')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = LogUpForm()

    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        surname = form.surname.data
        name = form.name.data
        patronym = form.patronym.data
        dateOfBirth = form.dateOfBirth.data

        db = get_db()
        db.execute(
            'INSERT INTO Users (login, password, surname, name, patronym, dateOfBirth) VALUES (?, ?, ?, ?, ?, ?)',
            (login, generate_password_hash(password), surname, name, patronym, dateOfBirth)
        )
        db.commit()
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LogInForm()

    if form.validate_on_submit():
        login = form.login.data

        db = get_db()
        user = db.execute(
            'SELECT * FROM Users WHERE login = ?', (login,)
        ).fetchone()

        session.clear()
        session['user_id'] = user['userID']
        return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


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
