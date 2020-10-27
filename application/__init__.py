import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis
import rq
from application.extensions import mail
import config

db = SQLAlchemy() 
migrate = Migrate()
login = LoginManager()
# mail = Mail()
 
def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)  
    app.config.from_object(config_class) 
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) 
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('securenotesapp-tasks', connection=app.redis)
    mail.init_app(app)

    from application.routes.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from application.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from application.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from application.routes.notes import bp as notes_bp
    app.register_blueprint(notes_bp)

    from application.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/noteapp.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Noteapp startup')

    from application.models.user import User
    from application.models.note import Note
    from application.models.post import Post

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Post': Post, 'Note': Note}

    return app

# from application.models.user import User
# from application.models.note import Note
# from application.models.post import Post



