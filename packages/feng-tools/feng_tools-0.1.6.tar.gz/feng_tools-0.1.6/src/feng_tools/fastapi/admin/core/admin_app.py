import sys

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError, ValidationException
from pydantic import ValidationError

from feng_tools.fastapi.admin.amis.AmisModelAdminPage import AmisModelAdminPage
from feng_tools.fastapi.admin.core.admin_app_info import AdminAppInfo
from feng_tools.fastapi.admin.core.admin_app_settings import AdminAppSettings
from feng_tools.fastapi.admin.core.model_admin_api import ModelAdminApi
from feng_tools.fastapi.admin.core.model_admin_settings import ModelAdminSettings
from feng_tools.fastapi.admin.page.model_admin_page import ModelAdminPage
from feng_tools.fastapi.api.api_response import ApiResponse
from feng_tools.fastapi.api.api_schemas import ApiEnum
from feng_tools.fastapi.api.api_tools import ApiTools
from feng_tools.fastapi.core.exception_handler import value_exception_handle, validation_exception_handle, \
    exception_handle
from feng_tools.sqlmodel import engine_tools, sqlmodel_tools


class AdminApp(FastAPI):

    def __init__(self, settings:AdminAppSettings,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        if self.settings.database_setting is None or settings.database_setting.url is None:
            print('请配置数据库连接：database_setting')
            sys.exit(1)
        self.db_engine = engine_tools.new_engine(settings.database_setting)
        sqlmodel_tools.init_db(self.db_engine)
        if hasattr(self.settings.file_handler, 'set_db_engine'):
            self.settings.file_handler.set_db_engine(self.db_engine)


    def register_exception_handlers(self, app: FastAPI):
        for tmp in [app, self]:
            tmp.add_exception_handler(RequestValidationError, handler=validation_exception_handle)
            tmp.add_exception_handler(ValueError, handler=value_exception_handle)
            app.add_exception_handler(ValidationException, handler=value_exception_handle)
            app.add_exception_handler(ValidationError, handler=value_exception_handle)
            tmp.add_exception_handler(Exception, exception_handle)
    def load_app(self, app: FastAPI,
                 admin_prefix:str=None,
                 admin_name: str = "admin",
                 enable_exception_handlers: bool = True):
        if admin_prefix:
            self.settings.prefix = admin_prefix
        app.mount(self.settings.prefix, self, name=admin_name)
        if enable_exception_handlers:
            self.register_exception_handlers(app)
        self._create_admin_page()
        self._create_file_api()

    def _create_admin_page(self):
        index_router = APIRouter()
        index_router.add_api_route(
            "/",
            self.settings.admin_app_page.get_html_response,
            methods=["GET"],
            name=ApiEnum.admin,
        )
        self.include_router(index_router)

    def _create_file_api(self):
        file_handler = self.settings.file_handler
        index_router = APIRouter(prefix='/file')
        index_router.add_api_route(
            "/upload/{file_type}",
            file_handler.upload_handle,
            methods=["POST", "PUT"],
            response_model=ApiResponse,
            name=ApiEnum.file_upload,
        )
        index_router.add_api_route(
            "/download/{file_id}",
            file_handler.download_handle,
            methods=["GET"],
            name=ApiEnum.file_upload,
        )
        self.include_router(index_router)

    def _create_model_admin_page(self, api_tools:ApiTools, model_admin_page_class: type[ModelAdminPage],
                                 model_admin_settings:ModelAdminSettings):
        """创建模型的管理页面"""
        if not model_admin_settings.has_page_api:
            return
        admin_app_info = AdminAppInfo(api_prefix=self.settings.prefix)
        api_tools.create_page_api(admin_app_info, model_admin_page_class, model_admin_settings)
        api_tools.create_json_api(admin_app_info, model_admin_page_class, model_admin_settings)

    def _create_model_admin_api(self, api_tools, model_admin_api_class: type[ModelAdminApi], model_admin_settings):
        """创建模型的管理api"""
        model_admin_api = model_admin_api_class(api_tools, self.db_engine,
                                                              model_admin_settings, self.settings)
        model_admin_api.create()

    def register_model_admin(self, model_admin_settings:ModelAdminSettings,
                             model_admin_page_class: type[ModelAdminPage] = AmisModelAdminPage,
                            model_admin_api_class: type[ModelAdminApi] = ModelAdminApi):
        """
        注册模型
        :param model_admin_settings:
        :param model_admin_page_class: model管理页面类（用于生成model的管理页面）
        :param model_admin_api_class: model管理API类（用于生成model的管理页面）
        """
        if not model_admin_settings.api_router:
            if not model_admin_settings.api_prefix:
                raise ValueError(f'请配置模型{model_admin_settings.model_class}的api_prefix')
            model_admin_settings.api_router = APIRouter(prefix=model_admin_settings.api_prefix)
        api_tools = ApiTools(api_router=model_admin_settings.api_router)

        # 创建模型的管理api
        self._create_model_admin_api(api_tools, model_admin_api_class, model_admin_settings)
        # 创建模型的管理页面
        self._create_model_admin_page(api_tools, model_admin_page_class, model_admin_settings)
        # 添加模型路由到管理app
        self.include_router(model_admin_settings.api_router)



