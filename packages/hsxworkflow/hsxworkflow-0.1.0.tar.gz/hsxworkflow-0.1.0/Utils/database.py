import aiomysql
import redis
from contextlib import asynccontextmanager
from typing import AsyncGenerator


class Database:
    def __init__(self, mysql_config: dict, redis_config: dict):
        self.mysql_config = mysql_config
        self.redis_config = redis_config
        self.redis_pool = None

    def init_redis(self):
        self.redis_pool = redis.ConnectionPool(host=self.redis_config['host'], port=self.redis_config['port'],
                                               max_connections=10, db=self.redis_config['db'],
                                               password=self.redis_config['password'])

    @asynccontextmanager
    async def mysql(self) -> AsyncGenerator[aiomysql.Connection, None]:
        conn = await aiomysql.connect(
            host=self.mysql_config['host'],
            port=self.mysql_config['port'],
            user=self.mysql_config['user'],
            password=self.mysql_config['password'],
            db=self.mysql_config['database'],
            cursorclass=aiomysql.DictCursor
        )
        try:
            yield conn
        finally:
            conn.close()

    @property
    def redis(self) -> redis.Redis:
        if not self.redis_pool:
            raise RuntimeError("Redis pool not initialized")
        return redis.Redis(connection_pool=self.redis_pool)
