# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏

from mangokit.assertion._custom_assertion import CustomAssertion
from mangokit.assertion._public_assertion import WhatIsItAssertion, ContainAssertion, MatchingAssertion, \
    WhatIsEqualToAssertion, PublicAssertion
from mangokit.assertion._sql_assertion import SqlAssertion
import sys

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")


class Assertion(WhatIsItAssertion, ContainAssertion, MatchingAssertion, WhatIsEqualToAssertion):
    pass


__all__ = [
    'Assertion',
    'CustomAssertion',
    'SqlAssertion',
    'PublicAssertion',
]
