# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏

from uiautomator2 import UiObject, UiObjectNotFoundError
from uiautomator2.exceptions import XPathElementNotFoundError
from uiautomator2.xpath import XPathSelector

from mangokit.enums import ElementExpEnum
from mangokit.exceptions import MangoKitError, ERROR_MSG_0031, ERROR_MSG_0022, ERROR_MSG_0020, \
    ERROR_MSG_0030, ERROR_MSG_0017, ERROR_MSG_0019, ERROR_MSG_0050, ERROR_MSG_0032, ERROR_MSG_0012, ERROR_MSG_0005
from mangokit.mangos import Mango
from mangokit.uidrive.android._application import AndroidApplication
from mangokit.uidrive.android._assertion import AndroidAssertion
from mangokit.uidrive.android._customization import AndroidCustomization
from mangokit.uidrive.android._element import AndroidElement
from mangokit.uidrive.android._equipment import AndroidEquipment
from mangokit.uidrive.android._page import AndroidPage

__all__ = [
    'AndroidApplication',
    'AndroidAssertion',
    'AndroidElement',
    'AndroidCustomization',
    'AndroidEquipment',
    'AndroidPage',
    'AndroidDriver',
]


class AndroidDriver(AndroidPage,
                    AndroidElement,
                    AndroidEquipment,
                    AndroidCustomization,
                    AndroidApplication):

    def __init__(self, base_data):
        super().__init__(base_data)

    def open_app(self):
        if not self.base_data.is_open_app:
            self.base_data.is_open_app = True
            self.a_press_home()
            self.a_app_stop_all()
            if self.base_data.android and self.base_data.package_name:
                self.a_start_app(self.base_data.package_name)

    def a_action_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'操作元素，名称：{name},key:{ope_key},value:{ope_value}')
        try:
            Mango.s_e(self, ope_key, ope_value)
        except ValueError as error:
            self.base_data.log.error(f'安卓自动化失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0012)
        except UiObjectNotFoundError as error:
            self.base_data.log.error(f'安卓自动化失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0032, value=(name,))
        except XPathElementNotFoundError as error:
            self.base_data.log.error(f'安卓自动化失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0050, value=(name,))

    def a_assertion_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'断言元素，名称：{name},key:{ope_key},value:{ope_value}')
        from mangokit.assertion import SqlAssertion
        from mangokit.assertion import PublicAssertion
        is_method = callable(getattr(AndroidAssertion(self.base_data), ope_key, None))
        is_method_public = callable(getattr(PublicAssertion, ope_key, None))

        if is_method or is_method_public:
            if ope_value['value'] is None:
                raise MangoKitError(*ERROR_MSG_0031, value=(name,))

        try:
            if is_method:
                self.base_data.log.debug(f'开始断言-1，方法：{ope_key}，断言值：{ope_value}')
                Mango.s_e(AndroidAssertion(self.base_data), ope_key, ope_value)
            elif is_method_public:
                self.base_data.log.debug(f'开始断言-2，方法：{ope_key}，断言值：{ope_value}')
                Mango.s_e(PublicAssertion, ope_key, ope_value)
            else:
                if self.base_data.mysql_connect is not None:
                    SqlAssertion.mysql_obj = self.base_data.mysql_connect
                    self.base_data.log.debug(f'开始断言-3，方法：sql相等端游，实际值：{ope_value}')
                    SqlAssertion.sql_is_equal(**ope_value)
                else:
                    raise MangoKitError(*ERROR_MSG_0019)
        except AssertionError as error:
            self.base_data.log.error(f'安卓自动化失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0017, value=error.args)
        except AttributeError as error:
            self.base_data.log.error(f'安卓自动化失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0030, )
        except ValueError as error:
            self.base_data.log.error(f'安卓自动化失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0005, )

    def a_find_ele(self, name, _type, exp, loc, sub) -> tuple[UiObject, int, str] | tuple[XPathSelector, int, str]:
        self.base_data.log.debug(
            f'查找元素，名称：{name},_type:{_type},exp:{exp},loc:{loc},sub:{sub}')
        match exp:
            case ElementExpEnum.LOCATOR.value:
                try:
                    if loc[:5] == 'xpath':
                        loc = eval(f"self.android.{loc}")
                    else:
                        loc = eval(f"self.android{loc}")
                except SyntaxError:
                    raise MangoKitError(*ERROR_MSG_0022)
            case ElementExpEnum.XPATH.value:
                loc = self.base_data.android.xpath(loc)
            case ElementExpEnum.BOUNDS.value:
                loc = self.base_data.android(text=loc)
            case ElementExpEnum.DESCRIPTION.value:
                loc = self.base_data.android(description=loc)
            case ElementExpEnum.RESOURCE_ID.value:
                loc = self.base_data.android(resourceId=loc)
            case _:
                raise MangoKitError(*ERROR_MSG_0020)
        text = None
        try:
            text = self.a_get_text(loc)
        except Exception:
            pass
        return loc, loc.count, text
