import os

from flask import Flask


def create_app(test_config=None):
    # Создание и настройка приложения
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'testApp.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # apply the blueprints to the app
    from . import auth, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    # from . import auth
    # app.register_blueprint(auth.bp)
    #
    # from . import main
    # app.register_blueprint(main.bp)
    # app.add_url_rule('/', endpoint='index')

    # from . import test
    # app.register_blueprint(test.bp)
    # # app.add_url_rule('/', endpoint='test')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
