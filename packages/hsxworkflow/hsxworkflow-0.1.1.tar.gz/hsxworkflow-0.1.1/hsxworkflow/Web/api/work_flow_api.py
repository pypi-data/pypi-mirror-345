from flask import Blueprint, jsonify, request
from ..base_handler import workflow_required, get_workflow_manager

workflow_api_bp = Blueprint('workflow_api', __name__, url_prefix='/api')


@workflow_api_bp.route('/workflow/list')
@workflow_required
def workflow_status():
    manager = get_workflow_manager()
    # 获取工作流状态逻辑
    info_dict = {}
    for key, value in manager.get_work_objects().items():
        instance_info = value.get_current_workflow_info()
        WorkflowClass = instance_info.get("WorkflowClass")
        WorkflowGroup = instance_info.get("WorkflowGroup")
        if WorkflowClass not in info_dict:
            info_dict[WorkflowClass] = instance_info
        else:
            info_dict[WorkflowClass]["WorkflowGroup"].append(WorkflowGroup[0])
    info_list = list(info_dict.values())
    return jsonify(info_list)


@workflow_api_bp.route('/workflow/start', methods=['POST'])
@workflow_required
def start_workflow():
    manager = get_workflow_manager()
    
    req_json = request.get_json()
    if req_json is None:
        return jsonify({"error": "Invalid request"}), 400
    class_id = req_json.get("classId")
    if class_id is None or not isinstance(class_id, int):
        return jsonify({"error": "Invalid request"}), 400
    
    manager.start_workflow(class_id)
    return jsonify({"message": "Workflow started"})


@workflow_api_bp.route('/workflow/stop', methods=['POST'])
@workflow_required
def stop_workflow():
    manager = get_workflow_manager()

    req_json = request.get_json()
    if req_json is None:
        return jsonify({"error": "Invalid request"}), 400
    class_id = req_json.get("classId")
    if class_id is None or not isinstance(class_id, int):
        return jsonify({"error": "Invalid request"}), 400

    instance = manager.stop_workflow(class_id)
    return jsonify({"message": "Workflow started"})
