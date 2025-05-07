# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-30 13:12
# @Author : 毛鹏
import subprocess
from typing import Optional
from unittest.mock import MagicMock

import sys

if not sys.platform.startswith('win32'):
    WindowControl = MagicMock()
    print("警告: uiautomation 仅支持 Windows，当前环境已自动跳过")
else:
    import uiautomation as auto
    from uiautomation.uiautomation import WindowControl

from mangokit.uidrive._base_data import BaseData

class NewWindows:

    def __init__(self, win_path: str, win_title: str):
        self.win_path = win_path
        self.win_title = win_title
        self.windows: Optional[None | WindowControl] = None

    def new_windows(self):
        subprocess.Popen(self.win_path)
        self.windows = auto.WindowControl(ClassName='ApplicationFrameWindow', Name=self.win_title)
        return self.windows
