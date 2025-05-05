from abc import abstractmethod

from starlette.requests import Request
from starlette.responses import HTMLResponse


class AdminAppPage:
    """管理应哟个页面"""

    @abstractmethod
    def get_html_response(self, request: Request) -> HTMLResponse:
        pass
