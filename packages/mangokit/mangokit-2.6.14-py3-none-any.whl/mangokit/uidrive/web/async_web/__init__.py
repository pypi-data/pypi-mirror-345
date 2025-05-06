# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-04 21:42
# @Author : 毛鹏
import re

from playwright._impl._errors import TimeoutError, Error, TargetClosedError
from playwright.async_api._generated import Locator

from mangokit.assertion import SqlAssertion
from mangokit.enums import ElementExpEnum, ElementOperationEnum, StatusEnum
from mangokit.exceptions import *
from mangokit.mangos import Mango
from mangokit.uidrive._base_data import BaseData
from mangokit.uidrive.web.async_web._assertion import AsyncWebAssertion
from mangokit.uidrive.web.async_web._browser import AsyncWebBrowser
from mangokit.uidrive.web.async_web._customization import AsyncWebCustomization
from mangokit.uidrive.web.async_web._element import AsyncWebElement
from mangokit.uidrive.web.async_web._input_device import AsyncWebDeviceInput
from mangokit.uidrive.web.async_web._page import AsyncWebPage

re = re
__all__ = [
    'AsyncWebPage',
    'AsyncWebElement',
    'AsyncWebDeviceInput',
    'AsyncWebCustomization',
    'AsyncWebBrowser',
    'AsyncWebAssertion',
    'AsyncWebDevice',
]


class AsyncWebDevice(AsyncWebBrowser,
                     AsyncWebPage,
                     AsyncWebElement,
                     AsyncWebDeviceInput,
                     AsyncWebCustomization):

    def __init__(self, base_data: BaseData):
        super().__init__(base_data)

    async def open_url(self):
        if not self.base_data.is_open_url:
            self.base_data.log.debug(f'打开url，is_open_url：{self.base_data.is_open_url},url:{self.base_data.url}')
            await self.w_goto(self.base_data.url)
            self.base_data.is_open_url = True
        elif self.base_data.switch_step_open_url and self.base_data.page.url != self.base_data.url:
            await self.w_wait_for_timeout(1)
            self.base_data.log.debug(f'打开url，is_open_url：{self.base_data.is_open_url},url:{self.base_data.url}')
            await self.w_goto(self.base_data.url)

    async def web_action_element(self, name, ope_key, ope_value, ):
        self.base_data.log.debug(f'操作元素，名称：{name},key:{ope_key},value:{ope_value}')
        try:
            await Mango.a_e(self, ope_key, ope_value)
        except TimeoutError as error:
            self.base_data.log.error(f'WEB自动化操作失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0011, value=(name,))
        except TargetClosedError:
            self.base_data.setup()
            raise MangoKitError(*ERROR_MSG_0010)
        except Error as error:
            self.base_data.log.error(f'WEB自动化操作失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0032, value=(name,))
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化操作失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0012)

    async def web_assertion_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'断言元素，名称：{name},key:{ope_key},value:{ope_value}')
        from mangokit.assertion import PublicAssertion
        is_method = callable(getattr(AsyncWebAssertion, ope_key, None))
        is_method_public = callable(getattr(PublicAssertion, ope_key, None))
        try:
            if is_method:
                if ope_value.get('actual', None) is None:
                    traceback.print_exc()
                    raise MangoKitError(*ERROR_MSG_0031, value=(name,))
                self.base_data.log.debug(f'开始断言-1，方法：{ope_key}，断言值：{ope_value}')
                await Mango.a_e(AsyncWebAssertion(self.base_data), ope_key, ope_value)
            elif is_method_public:
                self.base_data.log.debug(f'开始断言-2，方法：{ope_key}，断言值：{ope_value}')
                Mango.s_e(PublicAssertion, ope_key, ope_value)
            else:
                if self.base_data.mysql_connect is not None:
                    SqlAssertion.mysql_obj = self.base_data.mysql_connect
                    self.base_data.log.debug(f'开始断言-3，方法：sql相等端游，实际值：{ope_value}')
                    await SqlAssertion.sql_is_equal(**ope_value)
                else:
                    raise MangoKitError(*ERROR_MSG_0019)
        except AssertionError as error:
            self.base_data.log.debug(f'WEB自动化断言失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0017, value=error.args)
        except AttributeError as error:
            self.base_data.log.error(f'WEB自动化断言失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0048)
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化断言失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0005)
        except TargetClosedError:
            self.base_data.setup()
            raise MangoKitError(*ERROR_MSG_0010)
        except Error as error:
            self.base_data.log.error(f'WEB自动化断言失败-4，类型：{type(error)}，失败详情：{error}')
            raise MangoKitError(*ERROR_MSG_0052, value=(name,), )

    async def web_find_ele(self, name, _type, exp, loc, sub, is_iframe) \
            -> tuple[Locator, int, str] | tuple[list[Locator], int, str]:
        self.base_data.log.debug(
            f'查找元素，名称：{name},_type:{_type},exp:{exp},loc:{loc},sub:{sub},is_iframe:{is_iframe}')
        if is_iframe != StatusEnum.SUCCESS.value:
            locator: Locator = await self.__find_ele(self.base_data.page, exp, loc)
            try:
                count = await locator.count()
                if _type == ElementOperationEnum.OPE.value and (count < 1 or locator is None):
                    raise MangoKitError(*ERROR_MSG_0029, value=(name, loc))
                loc = locator.nth(sub - 1) if sub else locator
                text = None
                try:
                    text = await self.w_get_text(loc)
                except Exception:
                    pass
                return loc, count, text
            except Error as error:
                self.base_data.log.error(f'WEB自动化查找元素失败-1，类型：{type(error)}，失败详情：{error}')
                raise MangoKitError(*ERROR_MSG_0041, )
        else:
            ele_list: list[Locator] = []
            for i in self.base_data.page.frames:
                locator: Locator = await self.__find_ele(i, exp, loc)
                try:
                    count = await locator.count()
                except Error as error:
                    self.base_data.log.error(f'WEB自动化查找元素失败-2，类型：{type(error)}，失败详情：{error}')
                    raise MangoKitError(*ERROR_MSG_0041, )
                if count > 0:
                    for nth in range(0, count):
                        ele_list.append(locator.nth(nth))
                else:
                    raise MangoKitError(*ERROR_MSG_0023)
            if not ele_list:
                raise MangoKitError(*ERROR_MSG_0023)
            if not ele_list and _type == ElementOperationEnum.OPE.value:
                raise MangoKitError(*ERROR_MSG_0029, value=(name, loc))
            try:
                count = len(ele_list)
                loc = ele_list[sub - 1] if sub else ele_list[0]
                text = None
                try:
                    text = await self.w_get_text(loc)
                except Exception:
                    pass
                return loc, count, text
            except IndexError:
                raise MangoKitError(*ERROR_MSG_0025, value=(len(ele_list),))

    async def __find_ele(self, page, exp, loc) -> Locator:
        match exp:
            case ElementExpEnum.LOCATOR.value:
                try:
                    return eval(f"await page.{loc}")
                except SyntaxError:
                    try:
                        return eval(f"page.{loc}")
                    except SyntaxError as error:
                        self.base_data.log.error(f'WEB自动化查找元素失败-3，类型：{type(error)}，失败详情：{error}')
                        raise MangoKitError(*ERROR_MSG_0022)
                    except NameError as error:
                        self.base_data.log.error(f'WEB自动化查找元素失败-4，类型：{type(error)}，失败详情：{error}')
                        raise MangoKitError(*ERROR_MSG_0060)
            case ElementExpEnum.XPATH.value:
                return page.locator(f'xpath={loc}')
            case ElementExpEnum.CSS.value:
                return page.locator(loc)
            case ElementExpEnum.TEXT.value:
                return page.get_by_text(loc, exact=True)
            case ElementExpEnum.PLACEHOLDER.value:
                return page.get_by_placeholder(loc)
            case _:
                raise MangoKitError(*ERROR_MSG_0020)
