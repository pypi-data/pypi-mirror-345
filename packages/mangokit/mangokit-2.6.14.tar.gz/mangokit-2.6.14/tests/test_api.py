# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-12 17:31
# @Author : 毛鹏
import asyncio
import unittest

from mangokit.apidrive import requests, async_requests


class TestApi(unittest.TestCase):

    def test_a(self):
        response = asyncio.run(async_requests.get('https://www.baidu.com'))
        assert response.text

    def test_s(self):
        response = requests.get('https://www.baidu.com')
        assert response.text
