import os
import secrets

from flask import Flask, send_from_directory
from flask_cors import CORS
from .api.work_flow_api import workflow_api_bp
from .page.index import workflow_web_bp
from .socket.workflow_socket import init_workflow_socket


# from .page.views import init_views
def init_views(app):
    # 其他API端点...
    app.register_blueprint(workflow_web_bp)

def init_workflow_api(app):
    # 其他API端点...
    app.register_blueprint(workflow_api_bp)


def create_app(workflow_manager=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(current_dir, 'templates'),  # 表示在当前目录 (myproject/A/) 寻找模板文件
                static_folder=os.path.join(current_dir, 'assets'),  # 表示为上级目录 (myproject/) 开通虚拟资源入口
                static_url_path='',  # 这是路径前缀, 个人认为非常蛋疼的设计之一, 建议传空字符串, 可以避免很多麻烦
                )
    CORS(app)
    secret_key = secrets.token_hex(24)
    app.config['STATIC_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # 缓存时间为1小时
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secret_key  # 设置一个默认的密钥
    # 配置应用
    app.config['WORKFLOW_MANAGER'] = workflow_manager

    @app.route('/assets/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)

    # 初始化蓝图
    init_workflow_api(app)
    socket_app = init_workflow_socket(app)
    init_views(app)

    return socket_app, app
