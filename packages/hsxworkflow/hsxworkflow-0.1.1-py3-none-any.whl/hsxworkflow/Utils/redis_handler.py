import pickle
import time

from database import Database


class RedisHandler(Database):
    def __init__(self, rds_conf: dict, async_: bool = False):
        super().__init__(mysql_config={}, redis_config=rds_conf)
        self.init_redis()
        self.rds_conn = self.redis

    @staticmethod
    def get_keyname(key):
        current_time = time.strftime("%Y%m%d", time.localtime())
        keyname_ = f'{key}_{current_time}'
        return keyname_

    def has_key(self, key):
        return self.rds_conn.get(self.get_keyname(key))

    # 获取计数
    def get_count(self, key):
        num = self.rds_conn.get(self.get_keyname(key))
        if num:
            return int(num)
        return None

    def set_count(self, key, num=1):
        self.rds_conn.incr(self.get_keyname(key), num)

    def set_count_format_at_datetime(self, key):
        keyname_ = self.get_keyname(key)
        self.rds_conn.set(keyname_, 0, ex=60 * 60 * 48)  # key有效期24小时
        return keyname_

    def get_queue_len(self, queue_name):
        return self.rds_conn.llen(queue_name)

    def get_data_from_queue(self, queue_name):
        Pdata = self.rds_conn.rpop(queue_name)
        if Pdata and type(Pdata) == bytes:
            data = pickle.loads(Pdata)
            return data
        return None

    def save_data_to_queue(self, queue_name,data ,expire=60 * 60 * 24 * 7):
        Pdata = pickle.dumps(data)
        self.rds_conn.lpush(queue_name, Pdata)
        self.rds_conn.expire(queue_name, expire)


# RDB = RedisHandler({"host": "127.0.0.1", "port": 6379, "password": "", "db": 8})
RDB = RedisHandler({"host": "r-7xvlw8mvzsrtyku3scpd.redis.rds.aliyuncs.com", "port": 6379, "password": "redis+123", "db": 6})
