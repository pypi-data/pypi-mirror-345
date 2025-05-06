import json
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Optional, Any, Dict, Literal, TypeVar

T = TypeVar('T')


class StepStatus(Enum):
    """步骤执行状态枚举"""
    SUCCESS = 1  # 成功
    FAILURE = 2  # 失败
    ERROR = 44  # 错误
    IN_PROGRESS = 55  # 进行中
    STOP = 99  # 手动停止
    PENDING = 66  # 待处理
    SKIPPED = 77  # 已跳过
    TIMEOUT = 88  # 超时
    PAUSE = 100  # 暂停

    @classmethod
    def get_value_name(cls, value):
        value_map = cls._value2member_map_
        value_name = value_map.get(value)
        return value_name.name if value_name else None

    @classmethod
    def set_new_status(cls, name, value):
        # Check if the name is already used
        # if name in cls._member_names_:
        #     raise ValueError(f"Name '{name}' already exists in the enum")

        # Check if the value is already used
        if value in cls._value2member_map_:
            return cls._value2member_map_.get(value)

        # Create a new enum member
        new_member = cls.create_pseudo_member_new_(name, value)

        # Update enum mappings
        cls._member_names_.append(name)
        cls._member_map_[name] = new_member
        cls._value2member_map_[value] = new_member

        return new_member

    @classmethod
    def create_pseudo_member_new_(cls, name, value):
        """Helper method to create a new enum member dynamically"""
        new_member = object.__new__(cls)
        new_member._name_ = name
        new_member._value_ = value
        return new_member


@dataclass
class StepMetadata:
    """步骤执行元数据"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # 执行时长(秒)
    retry_count: int = 0  # 重试次数


class GlobalDataManager:
    """线程安全的全局数据管理器"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = {}
                    cls._instance._data_lock = Lock()
        return cls._instance

    def get(self, key: str, default: T = None) -> T:
        """安全获取数据"""
        with self._data_lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """安全设置数据"""
        with self._data_lock:
            self._data[key] = value

    def update(self, **kwargs) -> None:
        """安全更新多个数据"""
        with self._data_lock:
            self._data.update(kwargs)

    def delete(self, key: str) -> None:
        """安全删除数据"""
        with self._data_lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        """清空所有数据"""
        with self._data_lock:
            self._data.clear()

    def to_dict(self) -> Dict[str, Any]:
        """获取数据副本"""
        with self._data_lock:
            return self._data.copy()


class StepResult:
    """
    增强版步骤执行结果封装
    功能特点:
    - 支持链式调用
    - 自动状态管理
    - 异常处理
    - 数据序列化
    """

    def __init__(
            self,
            status: StepStatus = StepStatus.PENDING,
            base_status: Optional[StepStatus] = StepStatus,
            data: Any = None,
            message: str = "",
            metadata: Optional[StepMetadata] = None,
            **extra_data
    ):
        self.base_status = base_status
        self.step_name = ""
        self._status = status
        self._data = data
        self.step_index = 0
        self._message = message
        self._metadata = metadata or StepMetadata()
        self._extra_data = extra_data
        self.next_step_params = {}
        self._exception: Optional[Exception] = None

    def dict_to_class(self, data: Dict[str, Any]) -> 'StepResult':
        """
        将字典数据更新到类实例中

        处理逻辑:
        1. 遍历字典中的每个键值对
        2. 如果键对应类属性，则更新类属性
        3. 否则将键值对存入extra_data中

        特殊处理:
        - status字段: 需要将数值转换为StepStatus枚举值
        - metadata字段: 如果是字典，需要转换为StepMetadata对象

        :param data: 输入字典数据
        :return: 更新后的StepResult实例(支持链式调用)
        """
        if not isinstance(data, dict):
            return self

        for key, value in data.items():
            # 处理status字段
            if key == 'status':
                if isinstance(value, int):
                    if not hasattr(self.base_status, key):
                        self._status = self.base_status.set_new_status(name='UnknownStatus', value=value)
                    else:
                        self._status = getattr(self.base_status, key)
                elif isinstance(value, StepStatus):
                    self._status = value
                else:
                    raise TypeError(f"'status' can only be an int or StepResult")

            # 处理metadata字段
            elif key == 'metadata':
                if isinstance(value, dict):
                    self._metadata = StepMetadata(**value)
                elif isinstance(value, StepMetadata):
                    self._metadata = value
            # 处理其他标准属性
            elif key in {'data', 'msg', 'message'}:
                if key == 'msg': key = 'message'
                setattr(self, f'_{key}', value)
            # 处理exception字段
            elif key == 'exception':
                if isinstance(value, dict):
                    exc_type = value.get('type')
                    exc_msg = value.get('message')
                    if exc_type and exc_msg:
                        try:
                            # 尝试动态创建异常对象
                            exc_class = type(exc_type, (Exception,), {})
                            self._exception = exc_class(exc_msg)
                        except:
                            self._exception = Exception(exc_msg)
            # 其他字段存入extra_data
            else:
                self._extra_data[key] = value

        return self

    # 属性访问器
    @property
    def status(self) -> StepStatus:
        return self._status

    @property
    def data(self) -> Any:
        return self._data

    @property
    def message(self) -> str:
        return self._message

    @property
    def metadata(self) -> StepMetadata:
        return self._metadata

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    def start_timer(self) -> 'StepResult':
        """开始执行计时"""
        self._metadata.start_time = datetime.now()
        return self

    def stop_timer(self) -> 'StepResult':
        """结束执行计时"""
        if self._metadata.start_time:
            self._metadata.end_time = datetime.now()
            self._metadata.duration = (
                    self._metadata.end_time - self._metadata.start_time
            ).total_seconds()
        return self

    def record_exception(self, exc: Exception) -> 'StepResult':
        """记录执行异常"""
        self._exception = exc
        self._status = self.base_status.ERROR
        self._message = str(exc)
        return self.stop_timer()

    def to_dict(self, metadata: bool = False, extra_: Literal['merge', 'addition'] = 'addition') -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "step_name": self.step_name,
            "step_index": self.step_index,
            'status_msg': self._status.name,
            'status': self._status.value,
            'data': self._data,
            'msg': self._message
        }
        if extra_ == 'merge' and self._extra_data and isinstance(self._extra_data, dict):
            result.update(self._extra_data)
        else:
            result['extra_data'] = self._extra_data

        if metadata:
            result["metadata"] = asdict(self._metadata)

        if self._exception:
            result['exception'] = {
                'type': self._exception.__class__.__name__,
                'message': str(self._exception),
            }
        return result

    def to_json(self, **kwargs) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(**kwargs), default=str)

    def is_success(self) -> bool:
        """是否成功"""
        return self._status == self.base_status.SUCCESS

    def is_failure(self) -> bool:
        """是否失败"""
        return (self._status in {self.base_status.FAILURE, self.base_status.ERROR, self.base_status.TIMEOUT} or
                (not self.is_success() and self.is_completed()))

    def is_completed(self) -> bool:
        """是否已完成"""
        return self._status not in {self.base_status.PENDING, self.base_status.IN_PROGRESS}

    def is_stop(self) -> bool:
        return self._status == self.base_status.STOP

    def start_step_status(self) -> 'StepResult':
        self._status = self.base_status.IN_PROGRESS
        self.start_timer()
        return self

    def init_step_status(self) -> 'StepResult':
        self._status = self.base_status.PENDING
        return self

    # 状态操作方法
    def base_set_status(self, status: StepStatus, message: str = "", data: Any = None, **extra) -> 'StepResult':
        """设置执行状态"""
        self._status = status
        self._message = message
        self._data = data
        self._extra_data.update(extra)
        return self.stop_timer()


class ThreadController:
    def __init__(self, logger):
        self.condition = threading.Condition()
        self.logger = logger
        self.paused = False
        self.stopped = False  # 新增停止标志

    def pause(self):
        with self.condition:
            self.logger.info("暂停工作流")
            self.paused = True

    def resume(self):
        with self.condition:
            self.logger.info("继续工作流")
            self.paused = False
            self.condition.notify_all()  # 唤醒所有等待的线程

    def stop(self):
        with self.condition:
            self.logger.info("停止工作流")
            self.stopped = True  # 设置停止标志
            self.paused = False  # 确保线程能退出等待
            self.condition.notify_all()  # 唤醒所有线程

    def init(self):
        with self.condition:
            self.logger.info("初始化工作流")
            self.paused = False
            self.stopped = False

    def wait_if_paused(self):
        """检查是否暂停或停止，返回是否应该继续运行"""
        with self.condition:
            while self.paused and not self.stopped:
                self.condition.wait()  # 释放锁并等待通知
            return not self.stopped  # 如果停止则返回False
