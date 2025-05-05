from typing import Optional, Any, Literal, TypeVar, Generic
from pydantic import BaseModel, Field

_T = TypeVar("_T")

class HandleResult(BaseModel, Generic[_T]):
    """处理结果"""
    success:Optional[bool] = Field(default=True, description="是否成功")
    message:Optional[str] = Field(default='success', description="提示信息")
    data:Optional[_T] = Field(default=None, description="返回数据")



class EnumItem(BaseModel):
    # 是否是默认项
    is_default: Optional[bool] = False
    # 标题
    title: str = Field(default=None, title='枚举标题')
    description: Optional[str] = Field(default=None, title='枚举描述')
    value: Optional[str | int | float] = Field(default=None, title='枚举值')
    data_dict: Optional[dict[str, Any]] = Field(title='数据字典', default=dict())


class LinkItem(EnumItem):
    """链接项"""
    href: str = Field(title='链接地址')
    title: str = Field(title='链接标题')
    target: Optional[Literal['_blank', '_self', '_parent', '_top']] = '_self'
    code: Optional[str | int] = Field(default=None, title='编码')
    description: Optional[str] = Field(default=None, title='链接描述')
    image: Optional[str] = Field(default=None, title='链接图片')
    icon: Optional[str] = Field(default=None, title='链接图标')
    is_active: Optional[bool] = Field(title='是否激活', default=False)
    children: Optional[list['LinkItem']] = Field(title='子项', default=[])
    data_dict: Optional[dict[str, str | int | float]] = Field(title='数据字典', default=dict())
    is_ok: Optional[bool] = Field(title='是否可正常访问', default=True)
