from flask import jsonify, current_app
from functools import wraps

def get_workflow_manager():
    return current_app.config['WORKFLOW_MANAGER']


def workflow_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_workflow_manager() is None:
            return jsonify({"error": "Workflow manager not initialized"}), 500
        return f(*args, **kwargs)

    return decorated_function



