import inspect
import time
# 使用functools.partial绑定实例
from functools import partial
from time import sleep
from typing import Dict, Callable, Optional, Union, Any, TypeVar

from StepAction import StepActionHandler
from StepActionUtils import StepResult
from ..Utils.handler import quantity_detection_handler

T = TypeVar('T', bound=StepActionHandler)


def _handler_kwargs(func, kwargs):
    sig = inspect.signature(func)
    parameters = sig.parameters
    params_dict = {
        param: kwargs.get(param, None)
        for param in parameters
        if param in kwargs
    }
    return params_dict


class WorkDataHandler:
    """用于在不同模式下执行工作流任务的处理程序。支持多种执行模式，包括单次运行，无限循环，遍历数据结构和自定义工作流。
    """

    def __init__(self, time_interval: float = 1.0):
        """初始化WorkDataHandler
        Args:
            time_interval: 执行之间的睡眠间隔（以秒为单位）。默认为1.0。
        """
        self.TimeInterval = time_interval
        self._global_result: Dict[str, StepResult] = {}

    def _TraversalWork(self, cls_: T, **kwargs) -> Optional[StepResult]:
        """通过遍历所提供的数据来执行工作流。
        Args:
            cls_: StepActionHandler实例
            kwargs: 附加参数包括要遍历的‘data’
        Returns:
            Last StepResult，如果执行中断，则为None
        Raises:
            ValueError: 如果不支持遍历数据类型
        """
        traversal_data = kwargs.get("work_data")
        if traversal_data is None:
            raise ValueError("traversal_data must be provided")

        last_result = None

        if isinstance(traversal_data, dict):
            for data_key, data_value in traversal_data.items():
                res = self.run_func(cls_, traversal_={data_key: data_value})
                if res is False or res.is_stop():
                    break
                last_result = res

        elif isinstance(traversal_data, (list, tuple)):
            for data_value in traversal_data:
                res = self.run_func(cls_, traversal_=data_value)
                if res is False or res.is_stop():
                    break
                last_result = res
        else:
            raise ValueError(f"Unsupported traversal_data type: {type(traversal_data)}")

        return last_result

    def _QueueWork(self) -> None:
        """基于队列的工作流执行（待实现）。"""
        raise NotImplementedError("QueueWork is not yet implemented")

    def _IndefinitelyWork(self, cls_: T, *args, **kwargs) -> StepResult:
        """无限期地执行工作流，直到返回False。
        Args:
            cls_: StepActionHandler实例
        Returns:
            循环退出时的最终StepResult
        """
        while True:
            res = self.run_func(cls_, *args, **kwargs)
            if res is False or res.is_stop():
                break
        return self._global_result[cls_.WorkflowName]

    def run_func(self, cls_: T, *args, **kwargs) -> Union[StepResult, bool]:
        """执行工作流的所有步骤。
        Args:
            cls_: StepActionHandler实例
        Returns:
            StepResult : 如果数量检测失败则为False
        Raises:
            RuntimeError: 如果工作流执行失败
        """

        if cls_.execution_result.is_stop():
            # 如果工作流已经停止，则返回False
            return False
        if not quantity_detection_handler(self):
            return False

        try:
            res = cls_.run_all_steps(*args, **kwargs)
            self._global_result[cls_.WorkflowName] = res
            sleep(self.TimeInterval)
            cls_.set_flow_run_count()  # 运行次数加1
            return res
        except Exception as e:
            cls_.func_logger.error(f"Workflow execution failed: {str(e)}")
            raise RuntimeError(f"Workflow execution failed: {str(e)}") from e

    def _CustomWork(self, cls_: T, *args, **kwargs) -> Any:
        """用于自定义工作流执行的占位符"""
        raise NotImplementedError("CustomWork must be implemented using set_custom_work")

    def set_custom_work(self, func: Callable) -> None:
        """设置自定义工作流功能。
        Args:
            func: 可调用，用作自定义工作流
        """

        if not callable(func):
            raise TypeError("Custom work must be a callable")
        func_name = func.__name__
        if not func_name.startswith("CustomOfSingle"):
            # 函数名称以"CustomOf"开头 , 为单个自定义工作处理器 ,否则为全局工作处理器
            func_name = "_CustomWork"

        setattr(self, func_name, partial(func, self))

    def start_workflow(self, cls: T, *args, **kwargs) -> Any:
        """按指定方式启动工作流执行。
        参数:
            cls: StepActionHandler实例
        返回:
            工作流执行的结果
        提出了:
            ValueError：如果指定了无效模式
            RuntimeError：如果工作流执行失败
        """
        if not cls:
            raise ValueError("StepActionHandler instance must be provided")
        mode = cls.runtype.get("mode")
        if not mode:
            raise ValueError("Workflow mode must be specified in runtype")

        kwargs["work_data"] = cls.runtype.get("data")
        cls.set_StepAction_status("running", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        cls.init_result()
        cls.controller.init()
        try:
            if mode == "single":
                res = cls.run_all_steps(*args, **kwargs)
                self._global_result[cls.WorkflowName] = res
                return res
            elif mode == "indefinitely":
                return self._IndefinitelyWork(cls, **kwargs)
            elif mode == "queue":
                return self._QueueWork()
            elif mode == "traversal":
                return self._TraversalWork(cls, **kwargs)
            elif mode == "custom":
                params_dict = _handler_kwargs(self._CustomWork, kwargs)
                return self._CustomWork(cls, **params_dict)
            elif mode.startswith("CustomOfSingle"):
                if not hasattr(self, mode):
                    raise ValueError(f"WorkDataHandler function '{mode}' not found or '{mode}' not register to "
                                     f"WorkDataHandler")
                custom_func = getattr(self, mode)
                params_dict = _handler_kwargs(self._CustomWork, kwargs)
                # print(f"{mode} custom_func: {custom_func}")
                return custom_func(cls, **params_dict)
            else:
                raise ValueError(f"Unsupported runtype mode: {mode}")
        except Exception as e:
            cls.func_logger.error(f"Workflow '{cls.WorkflowName}' failed in {mode} mode: {str(e)}")
            raise RuntimeError(f"Workflow execution failed: {str(e)}") from e
        finally:

            if cls.status_text != "error":
                # 不是异常的状态 ，默认都设置为 stopped
                cls.set_StepAction_status("stopped")
            cls.controller.init()
            cls.Init_class_value()
