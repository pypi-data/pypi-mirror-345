from flask import Blueprint, render_template

workflow_web_bp = Blueprint('workflow_web', __name__)


@workflow_web_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')
