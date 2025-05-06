# -*- coding: utf-8 -*-
"""
@Time : 2025/4/10 22:37
@Author : hsxisawd
@File : DPWorkFlow.py
@Project : dome1
@Des: 高级工作流管理类，用于注册和启动工作任务，提供线程安全的任务执行环境
"""
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List

from .Code.StepActionUtils import GlobalDataManager, StepResult
from .Code.WorkFlowHandler import WorkDataHandler
from .Code.WorkRegister import WorkRegisterHandler
from .Web.flask_main import create_app


class WorkflowManager(WorkRegisterHandler):
    """
    高级工作流管理类，负责管理多个工作任务的注册和执行流程
    """
    _global_data = GlobalDataManager()

    def __init__(self, WorkData: WorkDataHandler = WorkDataHandler, max_workers: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._workflow_process = None
        self._web_process = None
        self.WorkDataHandler = WorkData()
        self.th_work = ThreadPoolExecutor(max_workers=max_workers)
        self.work_status = {}

    def register_object(self, WRH: WorkRegisterHandler):
        """
        注册对象
        :param WRH: WorkRegisterHandler对象
        """
        WRH.generate_step_action_list()
        self._work_objects.update(WRH.get_work_objects())

    def stop_workflow(self, work_id: int = None):

        if not self._work_objects:
            raise RuntimeError("没有注册任何工作任务，无法启动工作流")

        if work_id is not None:
            work_obj = self._work_objects.get(work_id)
            if not work_obj:
                raise RuntimeError(f"{work_id} 不存在任务中...")
            work_obj.set_stop()
            while work_obj.status_text == "running":
                print(work_obj.status_text)
                print("等待 任务停止！")
                time.sleep(1)
            return work_obj
        raise RuntimeError("请指定要停止的工作流ID")

    def start_workflow(self, work_id: int = None):
        """
        启动工作流执行
        根据配置决定是顺序执行还是并行执行工作任务
        """

        if not self._work_objects:
            raise RuntimeError("没有注册任何工作任务，无法启动工作流")

        def start_workflow_(cls):
            Work_obj = self.WorkDataHandler
            return Work_obj.start_workflow(cls=cls)

        if work_id is not None:
            work_obj = self._work_objects.get(work_id)
            if not work_obj:
                raise RuntimeError(f"{work_id} 不存在任务中...")
            self._futures = [self.th_work.submit(start_workflow_, work_obj)]
        else:
            self._futures = [self.th_work.submit(start_workflow_, obj) for ids, obj in self._work_objects.items()]

    def wait_result(self) -> List[StepResult]:
        """
           等待并获取所有工作流任务的结果
           Returns:
               List[StepResult]: 所有任务的结果列表，按提交顺序返回
           Raises:
               如果任何任务抛出异常，会在这里重新抛出
        """
        if not hasattr(self, '_futures'):
            raise RuntimeError("请先调用start_workflow()启动工作流")

        # 如果单任务直接执行，futures中是直接结果
        if len(self._work_objects) == 1:
            return [self._futures[0]]

        # 多线程情况，获取所有结果（会阻塞直到所有任务完成）
        return [future for future in self._futures]

    def run_flask_app(self):
        # app = create_app(workflow_manager)
        # app.run(host='0.0.0.0', port=5050, debug=True)
        # return
        socketio, app = create_app(self)
        socketio.run(app, host='0.0.0.0', port=5050, debug=False, allow_unsafe_werkzeug=True)
