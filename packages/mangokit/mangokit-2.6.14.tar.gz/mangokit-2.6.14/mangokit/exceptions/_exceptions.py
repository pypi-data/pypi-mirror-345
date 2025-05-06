# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time: 2023-07-16 15:17
# @Author : 毛鹏
import traceback


class MangoKitError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None):
        self.msg = msg.format(*value) if value else msg
        self.code = code

    def __str__(self):
        return f"[{self.code}] {self.msg}"


def main(a, b):
    return a + b


if __name__ == '__main__':
    try:
        main(1, "1")
    except Exception as e:
        print(traceback.format_exc())
        raise e
    print(1+233)