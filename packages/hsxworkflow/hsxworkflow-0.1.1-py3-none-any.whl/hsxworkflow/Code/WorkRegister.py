import inspect
import threading
from functools import wraps
from typing import Dict, Type, List, Union, Callable, Tuple, Any, Optional

from StepAction import StepActionHandler
from StepActionUtils import StepStatus


def is_unbound_method(obj: Any) -> bool:
    """
    检查对象是否是未绑定的方法（函数或未绑定的方法）
    Args:
        obj: 要检查的对象
    Return:
        bool: 如果是未绑定的方法则返回True，否则返回False
    """
    return inspect.isfunction(obj) or (inspect.ismethod(obj) and obj.__self__ is None)


class WorkRegisterHandler:
    # 线程锁，确保注册过程的线程安全
    _registration_lock = threading.Lock()
    # 类级别的注册表，存储所有注册的工作类
    _registered_classes: Dict[str, Type[StepActionHandler]] = {}

    def __init__(self, step_key: str = "default", StatusModel: StepStatus = StepStatus, global_log: bool = True,
                 start_: bool = True, title: str = "", desc: str = "", group_info: dict = None, **kwargs):
        """
        初始化工作流管理器
        "single", "traversal", "indefinitely", "queue", "custom"
        """
        self._step_info = {}
        self.work_title = title
        self.work_desc = desc
        self.group_info = group_info if group_info is not None else {}
        self._futures = None
        self._step_key = step_key
        self._step_action_registry: Dict[str, List[Union[Callable, tuple]]] = {}
        self._step_actions: List[Union[Callable, str]] = []  # 步骤动作列表
        self._work_run_mode: Dict[str, Any] = {}
        self._work_objects: Dict[int, StepActionHandler] = {}  # 工作对象实例列表
        self._child_functions: List[Callable] = []
        self._child_step_actions: Dict[str, Union[Callable, dict]] = {}
        self._child_fail_stop_func: List[str] = []
        self._step_retry_: Dict[str, Tuple[int, int]] = {}
        self._step_status = StatusModel
        self._global_log = global_log
        self._start_ = start_
        self._kwargs = kwargs

    @classmethod
    def register_class(cls) -> Callable:
        """
        类注册装饰器，用于注册工作类

        Returns:
            Callable: 装饰器函数
        """

        def decorator(target_class: Type[StepActionHandler]) -> Type[StepActionHandler]:
            """
            实际的类注册装饰器
            Args:
                target_class: 要注册的类
            Returns:
                Type[StepActionHandler]: 返回原类
            """
            with cls._registration_lock:  # 确保线程安全的注册
                class_name = target_class.__name__
                if class_name in cls._registered_classes:
                    raise ValueError(f"类 '{class_name}' 已经注册")

                if not issubclass(target_class, StepActionHandler):
                    raise TypeError(f"注册的类 '{class_name}' 必须是 StepActionHandler 的子类")

                cls._registered_classes[class_name] = target_class
                return target_class

        return decorator

    def register_work_task(
            self,
            step_actions: Optional[List[Union[Callable, str]]] = None,
            work_class: Optional[Type[StepActionHandler]] = None,
            step_key: str = "default",
    ) -> None:
        """
        注册工作任务
        Args:
            step_actions: 工作步骤列表，可以是方法名或可调用对象
            work_class: 工作任务类，必须是 StepActionHandler 的子类
            step_key: 工作步骤的标识键
        Raises:
            TypeError: 如果 work_class 不是 StepActionHandler 的子类
            ValueError: 如果 step_actions 包含无效的方法名或类型
        """

        if work_class and not issubclass(work_class, StepActionHandler):
            raise TypeError("work_class 必须是 StepActionHandler 的子类")

        # 处理 StepActionHandler 的特殊情况
        if work_class is None or work_class == "StepActionHandler":
            work_instance = StepActionHandler()
            processed_step_actions = []
            for step_func in step_actions:
                if isinstance(step_func, str):
                    if not hasattr(work_instance, step_func):
                        raise ValueError(f"StepActionHandler 没有 '{step_func}' 方法")
                    processed_step_actions.append(step_func)
                elif is_unbound_method(step_func):
                    processed_step_actions.append(
                        work_instance.set_step_func_to_self(func=step_func)
                    )
                else:
                    raise TypeError("step_actions 必须包含字符串（方法名）或未绑定的方法")

            for func in self._child_functions:
                if is_unbound_method(func):
                    work_instance.set_step_func_to_self(func=func)
            step_actions = processed_step_actions
        else:
            work_instance = work_class()
        # 配置工作实例
        # print(self._work_run_mode)
        title = work_instance.title
        desc = work_instance.desc
        work_instance.title = title if title else self.work_title
        work_instance.desc = desc if desc else self.work_desc
        work_instance.step_action_list = step_actions
        work_instance.child_step_actions = self._child_step_actions
        work_instance.fail_stop_func = self._child_fail_stop_func
        work_instance._step_retry_dict = self._step_retry_
        work_instance.WorkflowName = step_key if step_key else 'default'  # 使用 step_key 作为工作流名称

        work_instance.runtype = self._work_run_mode.get(step_key, {"mode": "single", "data": ""})
        work_instance._step_info = self._step_info.get(f"{work_instance.__class__.__name__}<:>{step_key}", {})
        work_instance._group_info = self.group_info
        work_instance.handler_init(global_log=self._global_log, stepStatus=self._step_status)
        self._work_objects[id(work_instance)] = work_instance

    def generate_step_action_list(self) -> None:
        """
        根据注册信息生成步骤动作列表

        Raises:
            ValueError: 如果尝试使用未注册的类
        """
        if self._start_ is False:
            return
        # 设置工作流模式
        self._set_work_flow_mode()

        for composite_key, step_entries in self._step_action_registry.items():
            class_parts = composite_key.split("<:>")

            class_name, step_key = class_parts
            # print( class_name, step_key )
            if class_name not in self._registered_classes and class_name != "StepActionHandler":
                raise ValueError(f"类 '{class_name}' 未注册，请先使用 @WorkflowManager.register_class 装饰器注册")

            work_class = None if class_name == "StepActionHandler" else self._registered_classes[class_name]

            # 提取已排序的函数列表（去掉排序值）
            step_actions = [entry[0] for entry in step_entries]
            # print( step_actions)
            self.register_work_task(
                step_actions=step_actions,
                work_class=work_class,
                step_key=step_key
            )

    def _initialize_step_registration(self, func: Callable, sort: Optional[int] = None, step_key: str = "default",
                                      work_class: str = "StepActionHandler", **kwargs) -> None:
        """
        初始化步骤注册
        Args:
            func: 要注册的函数或方法
            step_key: 步骤键名，用于分组
            work_class: 所属工作类名
            sort: 排序值，None表示追加到最后，否则按值排序
        """
        registry_key = f"{work_class}<:>{step_key}"
        # 创建包含函数和排序值的元组
        func_entry = (func, sort if sort is not None else float('inf'))  # 使用inf表示无排序

        if registry_key not in self._step_action_registry:
            self._step_action_registry[registry_key] = [func_entry]
        else:
            self._step_action_registry[registry_key].append(func_entry)
            # 按排序值进行排序 (None/inf会被排到最后)
            self._step_action_registry[registry_key].sort(key=lambda x: x[1])
        func_name = func_entry[0]
        if isinstance(func_name, Callable):
            func_name = func_name.__name__
        if registry_key not in self._step_info:
            self._step_info[registry_key] = {}
        self._step_info[registry_key].update({func_name: kwargs})

    def _initialize_child_step_registration(self, ParentFunc: str, **kwargs):
        child_step_dict = {}
        step_key = kwargs.pop("step_key", "default")
        for key, value in kwargs.items():
            if key.upper() in self._step_status._member_names_:
                if is_unbound_method(value):
                    self._child_functions.append(value)
                    value_name = value.__name__
                else:
                    value_name = value
                child_step_dict[key.upper()] = value_name
        if not isinstance(ParentFunc, str):
            ParentFunc = ParentFunc.__name__

        self._child_step_actions[f"{step_key}_{ParentFunc}"] = child_step_dict

    def _step_decorator(self, func: Callable, child_func: bool = False, *args, **kwargs):
        qualname = func.__qualname__
        actual_func = func
        split_qualname = qualname.split(".")
        # 如果是类方法，提取类名和方法名
        if len(split_qualname) > 1:
            class_name = split_qualname[0]
            method_name = split_qualname[1]
            kwargs["work_class"] = class_name
            actual_func = method_name

        # 子步骤 执行失败 是否整个停止所有步骤
        child_fail_stop = kwargs.get("child_fail_stop", False)
        if child_fail_stop is True:
            self._child_fail_stop_func.append(qualname)

        # 步骤重试次数
        step_retry = kwargs.get("retry", 0)
        if step_retry and step_retry > 0:
            self._step_retry_[qualname] = (step_retry, kwargs.get("retry_interval", 0),)

        if child_func is False:
            self._initialize_step_registration(actual_func, **kwargs)
        self._initialize_child_step_registration(actual_func, **kwargs)

    def step_child(self, **kwargs) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._step_decorator(func, child_func=True, **kwargs)

            @wraps(func)
            def wrapper(*arg, **kwarg):
                return func(*arg, **kwarg)

            return wrapper

        return decorator

    def step(self, step_key: str = "default", sort: Optional[int] = None,
             retry: int = 0, retry_interval: int = 0, *args, **kwargs) -> Callable:
        """
        注册工作步骤的装饰器
        Args:
            sort : 排序
            step_key: 步骤标识键，用于分组
            retry : 重试次数
            retry_interval : 重试间隔
        Returns:
            Callable: 装饰器函数
        """

        def decorator(func: Callable) -> Callable:
            if step_key == "default":
                kwargs["step_key"] = self._step_key
            else:
                kwargs["step_key"] = step_key
            kwargs["sort"] = sort
            kwargs["retry"] = retry
            kwargs["retry_interval"] = retry_interval
            self._step_decorator(func, *args, **kwargs)

            @wraps(func)
            def wrapper(*arg, **kwarg):
                return func(*arg, **kwarg)

            return wrapper

        return decorator

    def step_many(self, step_many=None, *args, **kwargs) -> Callable:
        """
        注册工作步骤的装饰器
        Args:
            step_many : 排序
            step_key: 步骤标识键，用于分组
            retry : 重试次数
            retry_interval : 重试间隔
        Returns:
            Callable: 装饰器函数
        """
        default_step_many = {"default": {"retry": 0, "sort": 1, "retry_interval": 0}}
        if step_many is None:
            step_many = default_step_many.copy()
        elif isinstance(step_many, tuple) or isinstance(step_many, list):
            step_many = {i: default_step_many["default"] for i in step_many}
        elif isinstance(step_many, dict):
            step_many = step_many
        else:
            raise TypeError("step_many type error , must be tuple,list,dict or None")

        def decorator(func: Callable) -> Callable:
            for step_key, step_info in step_many.items():
                if step_key == "default":
                    step_info["step_key"] = self._step_key
                else:
                    step_info["step_key"] = step_key
                self._step_decorator(func, *args, **step_info)

            @wraps(func)
            def wrapper(*arg, **kwarg):
                return func(*arg, **kwarg)

            return wrapper

        return decorator

    def get_work_objects(self) -> dict:
        """
        获取工作对象列表
        Returns:
            List[StepActionHandler]: 工作对象列表
        """
        return self._work_objects

    def get_work_object_id_list(self) -> list:
        """
        根据键获取工作对象
        Args:
            key: 工作对象键
        Returns:
            StepActionHandler: 工作对象
        """
        return list(self._work_objects.keys())

    def get_work_object_info_by_id(self, class_id: int) -> dict:
        obj = self._work_objects.get(class_id)
        if obj is None:
            raise ValueError("Workflow object not found")
        return obj.get_current_workflow_info()

    def set_work_object_socket(self, class_id: int, socket_obj):
        """
        设置工作对象socket
        Args:
            class_id: socket_id
            socket_obj:
        """

        obj = self._work_objects.get(class_id)
        if obj is None:
            raise ValueError("Workflow object not found")
        if obj.flask_socket is not None and socket_obj is not None:
            return
        obj.flask_socket = socket_obj

    def _set_work_flow_mode(self):
        """
        设置工作流模式
        kwarg single traversal indefinitely queue
        """
        if self._start_ is False:
            return

        kw_key = ["single", "traversal", "indefinitely", "queue", "custom"]

        for param_key, param_value in self._kwargs.items():
            if param_key not in kw_key and not param_key.startswith("CustomOfSingle"):
                continue
            if isinstance(param_value, str):
                self._work_run_mode[param_value] = {"mode": param_key, "data": self._kwargs.get(f"{param_key}_data")}
            elif isinstance(param_value, tuple):
                for item in param_value:
                    self._work_run_mode[item] = {"mode": param_key, "data": self._kwargs.get(f"{param_key}_data")}
            elif isinstance(param_value, dict):
                for item_key, item_value in param_value.items():
                    self._work_run_mode[item_key] = {"mode": param_key, "data": item_value}
            elif isinstance(param_value, bool):
                if param_value is False:
                    break
                self._work_run_mode["default"] = {"mode": param_key, "data": self._kwargs.get(f"{param_key}_data")}
            else:
                raise ValueError(f"Invalid value for {param_key}: {param_value}")
