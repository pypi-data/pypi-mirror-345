# -*- coding: utf-8 -*-
"""
@Time : 2025/4/19 17:13
@Author : hsxisawd
@File : workflow_socket.py
@Project : HSXWorkFlow
@Des:
"""
from socket import SocketIO

from ..base_handler import get_workflow_manager
from flask_socketio import SocketIO, emit, join_room, leave_room


def init_workflow_socket(app):
    socketio = SocketIO(app, cors_allowed_origins='*')

    @socketio.on('connect')
    def handle_connect():
        work_flow = get_workflow_manager()
        now_work = work_flow.get_work_object_id_list()
        emit('connect_res', {'data': now_work})

    @socketio.on('disconnect')
    def handle_disconnect():
        try:
            print('Client disconnected')
            emit('disconnected_res', {'data': 200})
        except Exception as e:
            print(e)
        # work_flow = get_workflow_manager()
        # for ids, class_ in work_flow.get_work_objects().items():
        #     if class_.status_text == 'stopped':
        #         class_.status_text = 'standby'

    def handle_join(classId):
        if classId is None:
            return None
        return get_workflow_manager()

    @socketio.on('list')
    def on_list_data():
        info_dict = {}
        manager = get_workflow_manager()
        for key, value in manager.get_work_objects().items():
            instance_info = value.get_current_workflow_info()
            WorkflowClass = instance_info.get("WorkflowClass")
            WorkflowGroup = instance_info.get("WorkflowGroup")
            if WorkflowClass not in info_dict:
                info_dict[WorkflowClass] = instance_info
            else:
                info_dict[WorkflowClass]["WorkflowGroup"].append(WorkflowGroup[0])
        return {"code": 10000, "data": list(info_dict.values())}

    @socketio.on('start')
    def on_start(data):
        try:
            classId = int(data.get('classId', 0))
            work_flow = handle_join(classId)
            if classId is None:
                return {"code": 10001}
            work_flow.set_work_object_socket(classId, socketio)
            work_flow.start_workflow(classId)
            return {"code": 10000}
        except Exception as e:
            return {"code": 10001}

    @socketio.on('work_data')
    def on_work_data(data):
        try:
            classId = int(data.get('classId', 0))
            work_flow = handle_join(classId)
            if classId is None:
                return {"code": 10001}
            info = work_flow.get_work_object_info_by_id(classId)
            return {"code": 10000, "data": info}
        except Exception as e:
            return {"code": 10001}
    @socketio.on('stop')
    def on_stop(data):
        try:
            classId = int(data.get('classId', 0))
            work_flow = handle_join(classId)
            if classId is None:
                return {"code": 10001}
            work_flow.set_work_object_socket(classId, None)
            work_flow.stop_workflow(classId)
            return {"code": 10000}
        except Exception as e:
            return {"code": 10001}

    @socketio.on('join')
    def on_join(data):
        try:
            classId = int(data.get('classId', 0))
            work_flow = handle_join(classId)
            if classId is None:
                return {"code": 10001}
            if isinstance(classId, str):
                classId = int(classId)
            work_flow.set_work_object_socket(classId, socketio)
            # info = work_flow.get_work_object_info_by_id(classId)
            join_room(classId)
            return {"code": 10000}
        except Exception as e:
            return {"code": 10001}

    @socketio.on('leave')
    def on_leave(data):
        try:
            classId = int(data.get('classId', 0))
            work_flow = handle_join(classId)
            if classId is None:
                return {"code": 10001}
            work_flow.set_work_object_socket(classId, None)
            leave_room(classId)
            return {"code": 10000}
        except Exception as e:
            return {"code": 10001}

    return socketio
