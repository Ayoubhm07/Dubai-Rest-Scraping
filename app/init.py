from flask import Flask
from app.celery_instance import make_celery, celery


def create_app():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    make_celery(app)
    return app
