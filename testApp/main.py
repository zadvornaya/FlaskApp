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
    current_ques = request.args.get('ques', 1, type=int)

    db = get_db()

    # Получение формулировки вопроса
    question = db.execute(
        'SELECT * FROM Questions WHERE quesID = ?', (current_ques,)
    ).fetchone()
    # todo: Сделать ошибку рабочей
    # if question is None:
    #     abort(404, "Вопрос № {0} не существует.".format(question['quesID']))

    # Получение ответов
    answers = db.execute(
        "SELECT ansID, ansCont FROM Answers WHERE quesID = ?", (current_ques,)
    ).fetchall()
    ansData = db.execute(
        'SELECT COUNT(validity) AS ansCount, SUM(validity) AS ansSum  FROM Answers WHERE quesID = ?', (current_ques,)
    ).fetchone()

    if ansData['ansCount'] == 1 and ansData['ansSum'] == 1:
        form = TextForm()
    elif ansData['ansSum'] == 1:
        form = RadioForm(answers)
    else:
        form = CheckboxForm(answers)

    if form.validate_on_submit():
        flash("Прошло")
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
                (g.user['userID'], current_ques, ansID)
            )
            db.commit()

        db.execute(
            'UPDATE Users SET progress = ? WHERE userID = ?;',
            (current_ques + 1, g.user['userID'])
        )
        db.commit()

        return redirect(url_for('main.test', ques=current_ques + 1))

    return render_template("main/test.html", form=form, question=question, ansData=ansData)


def get_ques(quesID, check_progress=True):
    """Get a ques and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param quesID: id of ques to get
    :param check_progress: require the current user to be the author
    :return: the ques with author information
    :raise 404: if a ques with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    ques = get_db().execute("SELECT * FROM Questions WHERE quesID = ?", (quesID,), ).fetchone()

    if ques is None:
        abort(404, "Вопрос № {0} не существует.".format(quesID))

    # if check_progress and ques["author_id"] != g.user["id"]:
    #     abort(403)

    return ques

# @bp.route("/test", methods=("GET", "POST"))
# def test():
#     """Поочередно показывает вопросы."""
#     db = get_db()
#     questions = db.execute(
#         "SELECT quesID, ansID, quesCont, ansCont FROM Questions JOIN Answers USING(quesID);"
#     ).fetchall()
#     return render_template("main/test.html", questions=questions)
#
#
# @bp.route("/test", methods=("GET", "POST"))
# def test():
#     """Поочередно показывает вопросы."""
#     # pagination
#     current_ques = request.args.get('ques', 1, type=int)
#     # http://localhost:5000/?page=1
#     # http://localhost:5000/?page=2
#     # pages, per page
#     items_per_page = 20
#     questions = round(len(item_list) / items_per_page + .499)  # the .499 is for rounding to the upside
#     from_page = int(page) * items_per_page - items_per_page  # 36 per page
#     upto_page = int(page) * items_per_page
#
#     list_part = item_list[from_page:upto_page]
#
#     return render_template("main/test.html", list_part=list_part, pages=pages, current_page=current_page)
#
# def get_post(id, check_author=True):
#     """Get a post and its author by id.
#     Checks that the id exists and optionally that the current user is
#     the author.
#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     post = (
#         get_db()
#         .execute(
#             "SELECT p.id, title, body, created, author_id, username"
#             " FROM post p JOIN user u ON p.author_id = u.id"
#             " WHERE p.id = ?",
#             (id,),
#         )
#         .fetchone()
#     )
#
#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#
#     if check_author and post["author_id"] != g.user["id"]:
#         abort(403)
#
#     return post
#
#
# @bp.route("/create", methods=("GET", "POST"))
# @login_required
# def create():
#     """Create a new post for the current user."""
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
#                 (title, body, g.user["id"]),
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/create.html")
#
#
# @bp.route("/<int:id>/update", methods=("GET", "POST"))
# @login_required
# def update(id):
#     """Update a post if the current user is the author."""
#     post = get_post(id)
#
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/update.html", post=post)
#
#
# @bp.route("/<int:id>/delete", methods=("POST",))
# @login_required
# def delete(id):
#     """Delete a post.
#     Ensures that the post exists and that the logged in user is the
#     author of the post.
#     """
#     get_post(id)
#     db = get_db()
#     db.execute("DELETE FROM post WHERE id = ?", (id,))
#     db.commit()
#     return redirect(url_for("blog.index"))
