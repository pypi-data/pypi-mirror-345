from typing import Optional

from pydantic_settings import BaseSettings


from feng_tools.fastapi.admin.page.admin_app_page import AdminAppPage
from feng_tools.fastapi.admin.page.model_admin_page import ModelAdminPage
from feng_tools.fastapi.core.file_handler import FileHandler
from feng_tools.sqlalchemy.sqlalchemy_settings import DatabaseSettings


class AdminAppSettings(BaseSettings):
    # 管理应用的前缀
    prefix: Optional[str] = '/admin'
    # 数据库设置
    database_setting: DatabaseSettings = None
    # 管理应用的主体（用于生成app的主体页面）
    admin_app_page:AdminAppPage
    # 文件上传和下载处理类
    file_handler: FileHandler



