# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-23 16:55
# @Author : 毛鹏
import asyncio

from mangokit.apidrive import async_requests
from mangokit.data_processor import DataProcessor
from mangokit.database import MysqlConnect
from mangokit.log_collector import set_log
from mangokit.mangos import Mango
from mangokit.models import ResponseModel, MysqlConingModel
from mangokit.tools import project_dir


def test_001(is_send=False):
    if is_send:
        text = '哈哈哈，测试内容！'
        Mango.s(text)


def test_003():
    url = 'https://www.baidu.com/home/feed/feedwater?id=2&offset=1&sessionId=&crids=&req_type=1&bsToken=47b1e832d560175c274525ef2c36828d&pos=&newsNum=&needAd=1&refresh_state=-1&ismain=1&indextype=manht&_req_seqid=0xf534052f012fd953&asyn=1&t=1727853777386&sid=60271_60826_60784'
    assert requests.get(url).text == '{"errMsg":"缺失参数","errno":10000}'


def test_004():
    mysql_connect = MysqlConnect(MysqlConingModel(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mP123456&',
        database='mango_server',
    ))
    result = mysql_connect.execute('SHOW TABLES;')
    assert result is not None


def test_005():
    from mangokit.tools import project_dir
    print(project_dir.cache)
    connect = SQLiteConnect(fr'{project_dir.cache}\cache.db')
    connect.execute('''CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY, name TEXT)''')
    connect.execute("INSERT INTO my_table (name) VALUES ('test_name')")
    result = connect.execute("SELECT * FROM my_table WHERE name='test_name'")
    assert result is not None, "数据不存在"
    connect.execute("DROP TABLE my_table")


def test_006():
    value = 'haha'
    key = '${key}'
    processor = DataProcessor()
    Mango.s_e(processor, 'set_cache', {'key': 'key', "value": value})
    print(processor.replace(key))
    assert Mango.s_e(processor, 'replace', key) == value


def test_0066():
    key = '${{randint({"left": 1,"left"=2})}}'
    processor = DataProcessor()
    print(processor.replace(key))


def test_007():
    log = set_log(project_dir.logs())
    log.debug('DEBUG')
    log.info("INFO")
    log.warning("WARNING")
    log.error("ERROR")
    log.critical("CRITICAL")


def test_008():
    async def main():
        response: ResponseModel = await async_requests.post('https://www.wanandroid.com/user/login',
                                                            data={
                                                                "password": "729164035",
                                                                "username": "maopeng"
                                                            })

        print(response.json_data)

    asyncio.run(main())


if __name__ == '__main__':
    # test_001(True)
    # test_003()
    # test_004()
    # test_005()
    # test_006()
    # test_007()
    # test_008()
    test_0066()
