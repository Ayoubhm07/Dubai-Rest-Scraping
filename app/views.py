from flask import Blueprint, jsonify
from tasks import run_scheduled_task

main = Blueprint('main', __name__)


@main.route('/run-script', methods=['GET'])
def run_script():
    result = run_scheduled_task.delay()
    return jsonify({"status": "success", "task_id": result.id, "message": "Task initiated"})
