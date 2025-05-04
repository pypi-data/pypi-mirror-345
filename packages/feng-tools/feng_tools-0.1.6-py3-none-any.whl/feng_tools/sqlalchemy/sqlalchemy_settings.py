from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    # 数据库url,示例：'mysql+pymysql://root:123456@127.0.0.1:3306/face_attendance_db'
    # 数据库异步url，示例：'mysql+aiomysql://root:123456@127.0.0.1:3306/face_attendance_db'
    url: Optional[str] = None
    pool_size: Optional[int] = 5
    max_overflow: Optional[int] = 10
    pool_timeout: Optional[int] = 30
    pool_recycle: Optional[int] = 3600
    echo: Optional[int] = True
    echo_pool: Optional[str] = 'debug'
    pool_pre_ping: Optional[bool] = True