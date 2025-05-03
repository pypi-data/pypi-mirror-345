import time

import webview
from idepy.core import API
from idepy.core.main import get_app
import idepy.core.utils as utils
from idepy.web_utils.element_plus_utils import ElementPlusUtils
from zhuguang_sdk.core import ZhuguangSDK


class ZGThemeUtils:
    def show_login(self):
        wd = None

        class LoginAPI(API, ElementPlusUtils):

            def __init__(self):
                super().__init__()
                # 设置窗口初始数据
                self.web_data = { }

            def reg_account(self):
                zg: ZhuguangSDK = get_app().zg
                utils.open_url(zg.server_url)


            def get_data(self):
                return {}

            def get_qrcode_data(self):
                zg: ZhuguangSDK = get_app().zg
                return zg.login_qrcode_info()

            def login(self, username, password):
                zg: ZhuguangSDK = get_app().zg
                try:
                    r = zg.login(username, password)
                except Exception as e:
                    return str(e)
                self.close()

            def check_qrcode_status(self, ticket):
                zg: ZhuguangSDK = get_app().zg
                return zg.check_qrcode_login(ticket, self.close)
            def close(self):
                wd.destroy()

        window_config = {
            "title": "登录",
            "width": 400,
            "height": 320,
            "on_top": True,
            "focus": True,
            "resizable": False,
            "js_api": LoginAPI(),
            "url": "/window_sys/login/index.html"
        }
        wd = get_app().create_window(**window_config)

        while wd in webview.windows:
            time.sleep(0.3)

        zg: ZhuguangSDK = get_app().zg

        return zg.has_login()
