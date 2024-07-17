from celery import Celery


def make_celery(app):
    class ContextTask(Celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

        # Initialize Celery with Flask app's settings

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )

    # Update Celery's configuration with Flask app's configuration
    celery.conf.update(app.config)
    celery.Task = ContextTask

    return celery
