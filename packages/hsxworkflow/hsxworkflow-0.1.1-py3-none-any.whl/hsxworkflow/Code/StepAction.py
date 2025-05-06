import inspect
from time import sleep
from typing import Any, Optional, Generator, TypeVar, Union, Callable

from StepActionUtils import GlobalDataManager, StepStatus, StepResult, ThreadController
from ..Utils.handler import task_success_add_count
from ..Utils.logger import setup_logger, BASE_LOGGER

T = TypeVar('T')


class StepActionHandler:
    """
    步骤执行处理器
    功能特点:
    - 线程安全的全局数据管理
    - 自动最终状态处理
    - 完善的执行流程控制
    """
    _global_data = GlobalDataManager()
    _start_ = False

    def __init__(self):
        self._base_logger = None
        self.func_logger = None
        self.title = ""
        self.desc = ""
        self._group_info = {}
        self.step_action_list:Optional[list] = []
        self.child_step_actions = {}
        self.fail_stop_func = []
        self.runtype = {"mode": "single", "data": ""}
        self.traversal_data = None
        self.WorkflowName:Optional[str] = ""
        self.current_step: Optional[str] = None
        self._step_retry_dict = {}
        self.stepStatus = StepStatus
        self._execution_result = None
        self._finalized = False
        self.last_step = False
        self._global_result = {}
        self._step_info = {}
        self.status_text = "standby"  # 启动状态 standby 待机 running 运行中 stopped 已停止 error 异常
        self.start_time = "--"
        self.controller: Union[ThreadController, None] = None  # 线程控制器
        self.flask_socket = None
        self.flow_run_count = 0  # 流程运行次数

    def Init_class_value(self):
        self.status_text = "standby"  # 启动状态 standby 待机 running 运行中 stopped 已停止 error 异常
        self.start_time = "--"
        self.current_step = None
        self.flow_run_count = 0

    def init_result(self):
        self._execution_result = StepResult(base_status=self.stepStatus)
        # self.controller = ThreadController(self._base_logger)

    def set_flow_run_count(self):
        self.flow_run_count += 1
        if self.flask_socket:
            work_info = {
                "WorkflowID": id(self),
                "WorkflowRunCount": self.flow_run_count,
                "WorkflowCurrentStep": self.current_step,
            }
            self.flask_socket.emit("work_flow_count", work_info)
        return self.flow_run_count

    def set_StepAction_status(self, status: str, timer="--"):
        self.status_text = status
        self.start_time = timer
        if self.flask_socket:
            work_info = {
                "WorkflowID": id(self),
                "WorkflowStatus": self.status_text,
                "WorkflowStartTime": self.start_time,
                "WorkflowCurrentStep": self.current_step,
                "WorkflowRunCount": self.flow_run_count
            }
            self.flask_socket.emit("work_flow_list", work_info)

    def socket_log(self, msg: str, level: str = "i", base=False, **kwargs):
        if level not in self.func_logger.level_dict:
            raise ValueError("Invalid log level")
        if base is False:
            msg = f"{' ' * 10}{msg}"
        log_func, log_type = self.func_logger.level_dict[level]
        log_func(msg, **kwargs)
        if self.flask_socket:
            ids = id(self)
            self.flask_socket.emit("work_flow_step_log",
                                   {"WorkflowID": ids, "WorkflowLog": msg, "WorkflowLogType": log_type},
                                   room=ids)

    def socket_step_info(self):
        if self.flask_socket:
            ids = id(self)
            res_result = self._execution_result.to_dict()
            self.flask_socket.emit("work_flow_step_info",
                                   res_result,
                                   room=ids)

    def get_current_workflow_info(self) -> dict:
        # print(self.__dict__)
        """
        获取 当前实例的详细信息
        """

        def get_step_index(step):
            try:
                index = self.step_action_list.index(step)
                return index
            except ValueError:
                return None

        def get_step_info():
            step_info = []
            for key, value in self._step_info.items():
                steps = {"title": key}
                args = []
                for key_, value_ in value.items():
                    if key_ in ["desc", "retry", "retry_interval"]:
                        steps[key_] = value_
                    else:
                        args.append({"key_": key_.upper(), "value_": value_})
                steps["args"] = args
                step_info.append(steps)
            return step_info

        WorkflowGroupInfo = self._group_info.get(self.WorkflowName, {})
        workflow_info = {
            "WorkflowTitle": self.title,
            "WorkflowDesc": self.desc,
            "WorkflowClass": self.__class__.__name__,
            "WorkflowGroup": [{
                "WorkflowName": self.WorkflowName,
                "WorkflowID": id(self),
                "WorkflowRunType": self.runtype.get("mode", "single"),
                "WorkflowRunData": str(type(self.runtype.get("data")).__name__).upper(),
                "WorkflowStatus": self.status_text,
                "WorkflowResult": self._execution_result.to_dict(),
                "WorkflowCurrentStep": self.current_step,
                "WorkflowCurrentStepIndex": get_step_index(
                    self.current_step) if self.current_step is not None else None,
                "WorkflowStartTime": self.start_time,
                "WorkflowRunCount": self.flow_run_count,
                "WorkflowStepInfo": get_step_info(),
                **WorkflowGroupInfo
            }]}
        return workflow_info

    def handler_init(self, global_log: bool = True, stepStatus: StepStatus = StepStatus):
        if global_log:
            self._base_logger = BASE_LOGGER.logger
            self.func_logger = BASE_LOGGER
        else:
            log_ = setup_logger(name=f"{self.__class__.__name__}_{self.WorkflowName}")
            self._base_logger = log_.logger
            self.func_logger = log_

        self.stepStatus = stepStatus
        self._execution_result = StepResult(base_status=self.stepStatus)
        self.controller = ThreadController(self._base_logger)

    @property
    def execution_result(self):
        return self._execution_result

    def set_step_func_to_self(self, func: Callable):
        if not hasattr(self, func.__name__):
            setattr(self, func.__name__, func)
        return func.__name__

    def init_global_data(self, **kwargs):
        self._global_data.update(**kwargs)

    def set_success(self, message: str = "", data: Any = None, **extra) -> 'StepResult':
        """标记步骤为成功状态"""
        return self._execution_result.base_set_status(self.stepStatus.SUCCESS, message, data, **extra)

    def set_failure(self, message: str = "", data: Any = None, **extra) -> 'StepResult':
        """标记步骤为失败状态"""
        return self._execution_result.base_set_status(self.stepStatus.FAILURE, message, data, **extra)

    def set_error(self, message: str = "", data: Any = None, **extra) -> 'StepResult':
        """标记步骤为错误状态"""
        return self._execution_result.base_set_status(self.stepStatus.ERROR, message, data, **extra)

    def set_stop(self, message: str = "手动停止", data: Any = None, **extra) -> 'StepResult':
        """标记步骤为错误状态"""
        self.controller.stop()
        return self._execution_result.base_set_status(self.stepStatus.STOP, message, data, **extra)

    def set_pause(self, message: str = "手动暂停", data: Any = None, **extra) -> 'StepResult':
        """标记步骤为错误状态"""
        self.controller.pause()
        return self._execution_result.base_set_status(self.stepStatus.PAUSE, message, data, **extra)

    def _get_step_generator(self, step_action_list, *args, **kwargs) -> Generator[StepResult, None, None]:
        """获取步骤执行生成器（每次调用返回新的生成器）"""
        return self._create_step_generator(step_action_list, *args, **kwargs)

    @classmethod
    def get_global_data(cls, key: str, default: T = None) -> T:
        """获取全局共享数据"""
        return cls._global_data.get(key, default)

    @classmethod
    def set_global_data(cls, key: str, value: Any) -> None:
        """设置全局共享数据"""
        cls._global_data.set(key, value)

    @classmethod
    def update_global_data(cls, **kwargs) -> None:
        """更新全局共享数据"""
        cls._global_data.update(**kwargs)

    def run_child_step(self, current_step: str):
        step_key = f"{self.WorkflowName}_{current_step}"
        if not self.child_step_actions or step_key not in self.child_step_actions:
            return self._execution_result
        # print(self.child_step_actions)

        child_action_list = []
        current_step_child = self.child_step_actions[step_key]
        current_status = self._execution_result._status.name
        child_run = current_step_child.get(current_status)
        if child_run:
            child_action_list.append(child_run)
            return self.run_all_steps(step_action_list=child_action_list)
        return self._execution_result

    def _create_step_generator(self, step_action_list, *args, **kwargs) -> Generator[StepResult, None, None]:
        """创建步骤执行生成器"""
        next_param = {}
        step_len = len(step_action_list)
        # 执行步骤列表
        for index, step_name in enumerate(step_action_list):

            if self.controller.wait_if_paused() is False:  # 检查是否暂停
                yield self._execution_result
                return

            self.last_step = index == step_len - 1
            self.current_step = step_name
            self._execution_result.step_name = step_name
            self._execution_result.step_index = index
            self._execution_result = self._execution_result.start_step_status()

            if not hasattr(self, step_name):
                error_msg = f"Step '{step_name}' 不在 {self.__class__.__name__}"
                self.socket_log(error_msg, "e", True, exc_info=True)
                yield self.set_error(error_msg)
                return
            try:
                step_method = getattr(self, step_name)
                # 获取步骤方法的参数

                sig = inspect.signature(step_method)
                parameters = sig.parameters
                kwargs.update(next_param)
                params_dict = {
                    param: kwargs.get(param, None)
                    for param in parameters
                    if param in kwargs
                }
                self.socket_log(f"{self.WorkflowName} 开始执行步骤: {step_name}", "i", True)
                qualname = step_method.__qualname__
                retry_tuple = self._step_retry_dict.get(qualname, (0, 0,))
                retry = retry_tuple[0] if retry_tuple[0] and retry_tuple[0] > 0 else 1
                for _ in range(retry):
                    if _ != 0:
                        self.socket_log(f"{self.WorkflowName} Step: {step_name} 失败,开始执行重试 => 重试次数: {_}",
                                        "i", True)
                    if self.__class__.__name__ == 'StepActionHandler':
                        # 执行步骤方法并处理返回结果
                        result = step_method(self, **params_dict)
                    else:
                        result = step_method(**params_dict)
                    next_param = self._process_step_result(result)
                    if not self._execution_result.is_failure():
                        # 如果步骤成功，则跳出重试循环
                        break

                    if retry_tuple[1] and retry_tuple[1] > 0:
                        sleep(retry_tuple[1])

                # 确保结果已停止计时
                self._execution_result.stop_timer()

                self._execution_result = self.run_child_step(step_name)
                if self._execution_result.is_failure() and qualname in self.fail_stop_func:
                    return

                # 记录执行日志
                if self._execution_result.is_success():
                    self.socket_log(
                        f"{self.WorkflowName} Step '{step_name}' 执行完成 message:{self._execution_result.to_dict()}",
                        "i", True)
                else:
                    self.socket_log(
                        f"{self.WorkflowName} Step '{step_name}' 终止下一步骤: message:{self._execution_result.to_dict()}",
                        "e", True, exc_info=True)

                yield self._execution_result
                # 如果步骤失败则终止执行
                if self._execution_result.is_failure():
                    return

            except Exception as e:
                error_msg = f"{self.WorkflowName} 执行 '{step_name}' 步骤错误: {str(e)}"
                self.socket_log(error_msg, "e", True, exc_info=True)
                yield self._execution_result.record_exception(e)
                return

    def to_next_step_param(self, **kwargs) -> StepResult:
        """存储下一步的参数"""
        self._execution_result.next_step_params = kwargs
        return self._execution_result

    def _process_step_result(self, result: Any) -> Union[dict, None]:
        """处理步骤方法的返回结果"""
        if isinstance(result, StepResult):
            self._execution_result = result
        elif isinstance(result, StepStatus):
            self._execution_result._status = result
        elif isinstance(result, dict):
            if "status" not in result:
                raise ValueError("Step method returns dictionary must be included 'status' ")
            self._execution_result.dict_to_class(result)
        elif result is not None:
            self._execution_result._data = result
            self._execution_result._status = self.stepStatus.SUCCESS
        else:
            if not self._execution_result.is_completed():
                self._execution_result._status = self.stepStatus.SUCCESS
                self._execution_result._message = f"{self.current_step} 步骤未设置返回值，自动继续执行"

        return self._execution_result.next_step_params

    def _finalize_execution(self, result: StepResult) -> StepResult:
        """最终化执行结果"""
        if self._finalized:
            return result

        self._finalized = True

        # 如果已经处于最终状态，则不再修改
        if result.is_completed():
            return result

        # 根据执行情况设置最终状态
        if result.exception is not None:
            return self.set_error(result.message)
        elif result.status == self.stepStatus.IN_PROGRESS:
            return self.set_failure(f"{self.WorkflowName} 执行中断 {result.message}")
        else:
            return self.set_success(f"{self.WorkflowName} 所有步骤执行完成 {result.message}")

    def run_all_steps(self, *args, **kwargs) -> StepResult:
        """执行所有步骤并返回最终结果"""
        if self._base_logger is None or self._execution_result is None:
            raise ValueError("First call 'handle_init' to initialize the instance")
        final_result = self._execution_result

        # 没有获取到 step_action_list 则代表 此步骤为子步骤,不是主步骤
        step_action_list = kwargs.pop("step_action_list", None)
        if step_action_list is None:
            final_result.init_step_status()
            step_action_list = self.step_action_list
        try:
            for step_result in self._get_step_generator(step_action_list, *args, **kwargs):
                final_result = step_result
                self.socket_step_info()
                if step_result.is_failure():
                    break
            # 确保最终状态正确
            final_result = self._finalize_execution(final_result)
            print(final_result.to_dict())
            if final_result.is_success():
                # 统计任务成功数量
                task_success_add_count()
            else:
                self.socket_log(f"<{self.current_step}> 步骤执行失败: {final_result.message}", "e", True, exc_info=True)
            return final_result

        except Exception as e:
            error_msg = f"<{self.current_step}> 执行过程中出现意外错误: {str(e)}"
            self.socket_log(error_msg, "e", True, exc_info=True)
            return self._finalize_execution(self._execution_result.record_exception(e))

    def execute_next_step(self) -> Optional[StepResult]:
        """执行下一步并返回结果"""
        try:
            result = next(self._get_step_generator(self.step_action_list))
            if result.is_failure():
                result = self._finalize_execution(result)
            return result
        except StopIteration:
            self.socket_log("已执行所有步骤", 'i', True)
            return None
        except Exception as e:
            error_msg = f"执行步骤时出现意外错误: {str(e)}"
            self.socket_log(error_msg, "e", True, exc_info=True)
            return self._finalize_execution(self._execution_result.record_exception(e))
