from unittest.mock import MagicMock

import sys

if not sys.platform.startswith('win32'):
    WindowControl = MagicMock()
    print("警告: uiautomation 仅支持 Windows，当前环境已自动跳过")
else:
    from uiautomation.uiautomation import ButtonControl
from mangokit.uidrive._base_data import BaseData


class WinElement(BaseData):
    """元素操作"""

    def win_click(self, locating: ButtonControl):
        self.windows.ButtonControl(Name='五').Click(simulateMove=False)

    def win_input(self, locating: ButtonControl):
        locating.ButtonControl(Name='五')
