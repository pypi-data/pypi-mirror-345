## 示例
### 1、创建模型类
```python
from datetime import time, date
from enum import Enum

from sqlmodel import Field
from sqlmodel.main import FieldInfo

from feng_tools.sqlmodel.base_models import BaseModel


class UserStatus(Enum):
    activied = '已激活'
    no_activied = '未激活'

class User(BaseModel, table=True):
    """用户"""
    __tablename__ = "user"
    username: str = Field(title="用户名",nullable=False)
    password: str = Field(title="密码")
    phone: str = Field(title="手机号", nullable=False)
    image_url:str = Field(title='头相', default='https://suda.cdn.bcebos.com/amis/images/alice-macaw.jpg')
    start_time:time= Field(title="上班时间")
    start_date: date = Field(title="上班日")
    status: UserStatus = Field(title="状态", )
```
### 2、创建测试类
```python
import os.path

from fastapi import FastAPI

from admin_demo.models import User
from feng_tools.amis.app.amis_app_settings import AmisAppSettings
from feng_tools.fastapi.admin.amis.AmisAdminAppPage import AmisAdminAppPage
from feng_tools.fastapi.admin.core.admin_app import AdminApp
from feng_tools.fastapi.admin.core.admin_app_settings import AdminAppSettings
from feng_tools.fastapi.admin.core.model_admin_settings import ModelAdminSettings, create_exclude_fields
from feng_tools.fastapi.api.api_response import ApiResponse
from feng_tools.fastapi.core.local_file_handler import LocalFileHandler
from feng_tools.json import json_tools
from feng_tools.sqlalchemy.sqlalchemy_settings import DatabaseSettings

local_save_path = os.path.join(os.path.dirname(__file__), 'upload')
app = FastAPI()
admin_app_page = AmisAdminAppPage(AmisAppSettings(
    menu_api='/admin/menu.json'
))
admin_app_settings = AdminAppSettings(database_setting=DatabaseSettings(url='mysql+pymysql://root:123456@127.0.0.1:3306/test-db'),
                                      admin_app_page=admin_app_page,
                                        file_handler=LocalFileHandler(local_save_path=local_save_path))
admin_app= AdminApp(admin_app_settings)
admin_app.load_app(app)


add_exclude_fields = create_exclude_fields(['id', ])
list_exclude_fields = create_exclude_fields(['password', ])
admin_app.register_model_admin(ModelAdminSettings(api_prefix='/user',
                                                  page_title='用户管理',
                                                  model_class=User,
                                                   add_exclude_fields=add_exclude_fields,
                                                    list_exclude_fields=list_exclude_fields,
                                                           filter_fields={'username', 'start_date', 'status'})
                               )


@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}

@admin_app.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}

@admin_app.get("/menu.json")
def menu_json():
    json_file = os.path.join(os.path.dirname(__file__), 'meun.json')
    return ApiResponse(data={
        'pages': json_tools.read_json(json_file)
    })


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8088)
```
### meun.json
```json
[
      {
        "children": [
                {
        "label": "Home",
        "url": "/",
        "redirect": "/index/1"
      },{
            "label":"用户",
            "icon":"fa fa-sitemap",
            "url":"/admin/user/page",
            "schema":{"type":"iframe","src":"/admin/user/page"}
          },
          {
            "label":"用户json",
            "icon":"fa fa-sitemap",
            "url":"/admin/user/json",
            "schemaApi":{"url":"/admin/user/json","method":"get","data":{},"cache":300000}
          },
          {
            "label": "页面A",
            "url": "index",
            "schema": {
              "type": "page",
              "title": "页面A",
              "body": "页面A"
            },
            "children": [
              {
                "label": "页面A-1",
                "url": "1",
                "schema": {
                  "type": "page",
                  "title": "页面A-1",
                  "body": "页面A-1"
                }
              },
              {
                "label": "页面A-2",
                "url": "2",
                "schema": {
                  "type": "page",
                  "title": "页面A-2",
                  "body": "页面A-2"
                }
              },
              {
                "label": "页面A-3",
                "url": "3",
                "schema": {
                  "type": "page",
                  "title": "页面A-3",
                  "body": "页面A-3"
                }
              }
            ]
          },
          {
            "label": "页面B",
            "badge": 3,
            "badgeClassName": "bg-info",
            "schema": {
              "type": "page",
              "title": "页面B",
              "body": "页面B"
            }
          },
          {
            "label": "页面C",
            "schema": {
              "type": "page",
              "title": "页面C",
              "body": "页面C"
            }
          },
          {
            "label": "列表示例",
            "url": "/crud",
            "rewrite": "/crud/list",
            "icon": "fa fa-cube",
            "children": [
              {
                "label": "列表",
                "url": "/crud/list",
                "icon": "fa fa-list",
                "schemaApi": "get:/pages/crud-list.json"
              },
              {
                "label": "新增",
                "url": "/crud/new",
                "icon": "fa fa-plus",
                "schemaApi": "get:/pages/crud-new.json"
              },
              {
                "label": "查看",
                "url": "/crud/:id",
                "schemaApi": "get:/pages/crud-view.json"
              },
              {
                "label": "修改",
                "url": "/crud/:id/edit",
                "schemaApi": "get:/pages/crud-edit.json"
              }
            ]
          }
        ]
      },
      {
        "label": "分组2",
        "children": [
          {
            "label": "用户管理",
            "schema": {
              "type": "page",
              "title": "用户管理",
              "body": "页面C"
            }
          },
          {
            "label": "外部链接",
            "link": "http://baidu.gitee.io/amis"
          },
          {
            "label": "部门管理",
            "schemaApi": "${API_HOST}/api/amis-mock/mock2/service/form?tpl=tpl3"
          },
          {
            "label": "jsonp 返回示例",
            "schemaApi": "jsonp:/pages/jsonp.js?callback=jsonpCallback"
          }
        ]
      }
    ]
```
