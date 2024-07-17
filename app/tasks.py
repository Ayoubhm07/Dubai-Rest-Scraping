from app.init import celery
from selenium_scripts.scrapper import run_selenium_script


@celery.task
def run_scheduled_task():
    run_selenium_script()
