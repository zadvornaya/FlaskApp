from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired
from werkzeug.exceptions import abort

from testApp.auth import login_required
from testApp.db import get_db

bp = Blueprint('main', __name__)


# Формы для трех видов вопросов.
class TextForm(FlaskForm):
    textAns = StringField('Ответ:', validators=[DataRequired()])
    submit = SubmitField('Далее')


def RadioForm(ans, **kwargs):
    class StaticRadioForm(FlaskForm):
        pass

    StaticRadioForm.radioAns = RadioField(choices=[(ans[0]['ansID'], ans[0]['ansCont']),
                                                   (ans[1]['ansID'], ans[1]['ansCont']),
                                                   (ans[2]['ansID'], ans[2]['ansCont'])])
    StaticRadioForm.submit = SubmitField('Далее')

    return StaticRadioForm()


def CheckboxForm(ans, **kwargs):
    class StaticCheckboxForm(FlaskForm):
        pass

    for (i, answer) in enumerate(ans):
        setattr(StaticCheckboxForm, 'checkboxAns_%d' % i, BooleanField(label=answer['ansCont']))
    StaticCheckboxForm.submit = SubmitField('Далее')

    return StaticCheckboxForm()


@bp.route("/")
def index():
    """Показывает главное меню."""
    return render_template("main/index.html")


@bp.route("/test", methods=("GET", "POST"))
@login_required
def test():
    # Получение номера текущего вопроса из адреса
    currentQues = request.args.get('ques', 1, type=int)

    db = get_db()

    # Получение формулировки вопроса
    question = db.execute(
        'SELECT * FROM Questions WHERE quesID = ?', (currentQues,)
    ).fetchone()
    # Ошибка при переходе на несуществующий вопрос.
    if question is None:
        abort(404, "Вопрос № {0} не существует.".format(currentQues))

    # Получение общего количества вопросов
    quesCount = db.execute(
        'SELECT COUNT(quesID) AS quesCount FROM Questions;'
    ).fetchone()
    quesCount = quesCount['quesCount']

    # Ограничение доступа к пройденным вопросам или вопросам в неверном порядке.
    if g.user['progress'] > quesCount:
        flash("Вы уже завершили тестирование, Поздравляем!"
              .format(g.user['progress'], "http://127.0.0.1:5000" + url_for('index')))
        return redirect(url_for('index'))
    if g.user['progress'] != currentQues:
        abort(403, "Вы остановились на вопросе № {}. Чтобы продолжить, перейдите по ссылке {}."
              .format(g.user['progress'], "http://127.0.0.1:5000" + url_for('main.test', ques=g.user['progress'])))

    # Получение ответов
    answers = db.execute(
        "SELECT ansID, ansCont FROM Answers WHERE quesID = ?", (currentQues,)
    ).fetchall()
    ansData = db.execute(
        'SELECT COUNT(validity) AS ansCount, SUM(validity) AS ansSum  FROM Answers WHERE quesID = ?', (currentQues,)
    ).fetchone()

    # Создание формы для вопроса
    if ansData['ansCount'] == 1 and ansData['ansSum'] == 1:
        form = TextForm()
    elif ansData['ansSum'] == 1:
        form = RadioForm(answers)
    else:
        form = CheckboxForm(answers)

    # Обработка подтверждения формы
    if form.validate_on_submit():
        ansIDs = []

        # Случай с текстовым полем.
        if ansData['ansCount'] == 1 and ansData['ansSum'] == 1:
            ansID = None
            # Если введенное пользователем соответствует правильному ответу, сохряняется ID этого ответа.
            if form.textAns.data == answers[0]['ansCont']:
                ansID = answers[0]['ansID']
            ansIDs.append(ansID)

        # Случай с одним вариантом.
        elif ansData['ansSum'] == 1:
            ansIDs.append(form.radioAns.data)

        # Случай с несколькими вариантами.
        else:
            # Сохраняются ID отмеченных ответов.
            if form.checkboxAns_0.data:
                ansIDs.append(answers[0]['ansID'])
            if form.checkboxAns_1.data:
                ansIDs.append(answers[1]['ansID'])
            if form.checkboxAns_2.data:
                ansIDs.append(answers[2]['ansID'])
            if form.checkboxAns_3.data:
                ansIDs.append(answers[3]['ansID'])
            if form.checkboxAns_4.data:
                ansIDs.append(answers[4]['ansID'])

        for ansID in ansIDs:
            db.execute(
                'INSERT INTO Testing (userID, quesID, ansID) VALUES (?, ?, ?)',
                (g.user['userID'], currentQues, ansID)
            )
            db.commit()

        db.execute(
            'UPDATE Users SET progress = ? WHERE userID = ?;',
            (currentQues + 1, g.user['userID'])
        )
        db.commit()

        if g.user['progress'] + 1 > quesCount:
            return redirect(url_for('main.result'))
        else:
            return redirect(url_for('main.test', ques=currentQues + 1))

    return render_template("main/test.html", form=form, question=question, ansData=ansData)


@bp.route("/result", methods=("GET", "POST"))
@login_required
def result():
    db = get_db()

    # Получение общего количества вопросов
    quesCount = db.execute(
        'SELECT COUNT(quesID) AS quesCount FROM Questions;'
    ).fetchone()
    quesCount = quesCount['quesCount']

    # Ограничение доступа к странице результатов.
    if g.user['progress'] <= int(quesCount):
        abort(403, "Тестирование еще не завершено."
              .format(g.user['progress']))

    # Вычисление результата
    ansData = db.execute(
        'SELECT SUM(validity) AS ansSum, MAX(answered) AS ansDate FROM Testing JOIN Answers USING(ansID)'
    ).fetchone()
    resSum = db.execute(
        'SELECT SUM(validity) AS resSum FROM Answers'
    ).fetchone()

    res = int(ansData['ansSum'] / resSum['resSum'] * 100)

    return render_template("main/result.html", res=res, date=ansData['ansDate'])
