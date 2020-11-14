from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort

from testApp.auth import login_required
from testApp.db import get_db

bp = Blueprint('main', __name__)


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

    if request.method == "POST":
        ansID = request.form['field']
        # todo: Записать ответ на прошлй вопрос в БД. Обновить прогресс пользователя.
        db.execute(
            'INSERT INTO Testing (userID, quesID, ansID) VALUES (?, ?, ?)',
            (g.user['userID'], current_ques, ansID)
        )
        db.commit()
        return redirect(url_for('main.test', ques=current_ques+1))

    # Получение формулировки вопроса
    question = db.execute(
        'SELECT * FROM Questions WHERE quesID = ?', (current_ques,)
    ).fetchone()
    if question is None:
        abort(404, "Вопрос № {0} не существует.".format(question['quesID']))

    # Получение ответов
    answers = db.execute(
        "SELECT ansID, ansCont FROM Answers WHERE quesID = ?", (current_ques,)
    ).fetchall()
    ansData = db.execute(
        'SELECT COUNT(validity) AS ansCount, SUM(validity) AS ansSum  FROM Answers WHERE quesID = ?', (current_ques,)
    ).fetchone()

    return render_template("main/test.html", question=question, answers=answers, ansData=ansData)


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
