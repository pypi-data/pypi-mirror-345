# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import json
import os.path
import time
from urllib.parse import urlparse

from playwright._impl._errors import TimeoutError, Error

from mangokit.decorator.method_callback import sync_method_callback
from mangokit.exceptions import MangoKitError, ERROR_MSG_0013, ERROR_MSG_0049, ERROR_MSG_0058, ERROR_MSG_0059
from mangokit.models import MethodModel
from mangokit.uidrive._base_data import BaseData
from mangokit.tools import Meta


class SyncWebBrowser(metaclass=Meta):
    """浏览器操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('web', '浏览器操作', 1, [
        MethodModel(f='_time', p='请输入等待时间', d=True)])
    def w_wait_for_timeout(self, _time: int):
        """强制等待"""
        time.sleep(int(_time))

    @sync_method_callback('web', '浏览器操作', 1, [
        MethodModel(f='url', p='请输入URL', d=True)])
    def w_goto(self, url: str):
        """打开URL"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise MangoKitError(*ERROR_MSG_0049)
            self.base_data.page.goto(url, timeout=60000)
            time.sleep(2)
        except TimeoutError:
            raise MangoKitError(*ERROR_MSG_0013, value=(url,))
        except Error:
            raise MangoKitError(*ERROR_MSG_0058, value=(url,))

    @sync_method_callback('web', '浏览器操作', 2, [MethodModel(f='path', p='请输入截图保存路径', d=True)])
    def w_screenshot(self, path: str):
        """整个页面截图"""
        self.base_data.page.screenshot(path=path, full_page=True)

    @sync_method_callback('web', '浏览器操作', 3)
    def w_alert(self):
        """设置弹窗不予处理"""
        self.base_data.page.on("dialog", lambda dialog: dialog.accept())

    @sync_method_callback('web', '浏览器操作', 4)
    def w_get_cookie(self):
        """获取cookie"""
        with open(os.path.join(self.base_data.download_path, 'storage_state.json'), 'w') as file:
            file.write(json.dumps(self.base_data.context.storage_state()))

    @sync_method_callback('web', '浏览器操作', 5, [
        MethodModel(f='storage_state', p='请输入获取cookie方法中获取的内容', d=True)])
    def w_set_cookie(self, storage_state: str):
        """设置cookie"""
        if isinstance(storage_state, str):
            storage_state = json.loads(storage_state)
        else:
            raise MangoKitError(*ERROR_MSG_0059)
        self.base_data.context.add_cookies(storage_state['cookies'])
        for storage in storage_state['origins']:
            local_storage = storage.get('localStorage', [])
            session_storage = storage.get('sessionStorage', [])
            for item in local_storage:
                self.base_data.context.add_init_script(
                    f"window.localStorage.setItem('{item['name']}', '{item['value']}');")
            for item in session_storage:
                self.base_data.context.add_init_script(
                    f"window.sessionStorage.setItem('{item['name']}', '{item['value']}');")
        self.base_data.page.reload()

    @sync_method_callback('web', '浏览器操作', 6)
    def w_clear_cookies(self):
        """清除所有cookie"""
        self.base_data.context.clear_cookies()

    @sync_method_callback('web', '浏览器操作', 7)
    def w_clear_storage(self):
        """清除本地存储和会话存储"""
        self.base_data.page.evaluate("() => localStorage.clear()")
        self.base_data.page.evaluate("() => sessionStorage.clear()")
