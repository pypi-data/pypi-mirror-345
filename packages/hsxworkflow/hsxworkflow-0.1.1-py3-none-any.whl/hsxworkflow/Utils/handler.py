from time import sleep

from redis_handler import RDB

QUANTITY_DETECTION = False
QUANTITY_DETECTION_BREAK = True
QUANTITY_DETECTION_MAX_ARRIVAL_TIME = 1000
QUANTITY_DETECTION_SLOW_DOWN = 1
QUANTITY_DETECTION_KEY = "MiGuKG_success:count"


def task_success_add_count(num=1):
    if QUANTITY_DETECTION:
        RDB.set_count(QUANTITY_DETECTION_KEY, num)


def quantity_detection_handler(self):
    """
    到量检测
    :return:
    """
    try:
        if QUANTITY_DETECTION:
            success_count = RDB.get_count(QUANTITY_DETECTION_KEY)
            self.WorkDataLogger.info(f"数量检测：{success_count}")
            if success_count is None:
                # 如果没有这个key，则初始一个值
                if not RDB.has_key(QUANTITY_DETECTION_KEY):
                    RDB.set_count_format_at_datetime(QUANTITY_DETECTION_KEY)
                    return True

            # 如果检测到量，则 休眠 指定时间 或者 结束执行程序
            if success_count >= int(QUANTITY_DETECTION_MAX_ARRIVAL_TIME):
                self.WorkDataLogger.info(f"数量检测：{success_count}，已到达最大值")
                if QUANTITY_DETECTION_BREAK:
                    return False
                sleep(QUANTITY_DETECTION_SLOW_DOWN)
        return True
    except Exception as e:
        self.WorkDataLogger.error(f"数量检测异常：{e}")
        return True
