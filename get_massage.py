import time
import requests
import re
import send_massage
from functools import wraps
import pywintypes
import win32api


def fun_run_time(func):
    @wraps(func)
    def inner(*args, **kwargs):
        s_time = time.time()
        ret = func(*args, **kwargs)
        e_time = time.time()
        print("{} cost {} s ".format(func.__name__, e_time-s_time))
        return ret
    return inner


def get_ma_mun(string, keys):
    """
    string为待匹配字段
    keys为关键字list
    """
    ck = []
    num = 0
    for i in keys:
        if i in string:
            num += 1
            ck.append(i)
    return num, ck


@fun_run_time
def get_to_send(keys, ini_js):
    url = 'https://www.cls.cn/telegraph'
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.47'
    }

    http = requests.get(url=url, headers=header)
    text = http.content.decode()
    text = re.findall('<span class="c-34304b">(.*?)</span>', text, re.S)[:17]
    text = [i.replace('<strong>', '').replace('</strong>', '\n') for i in text]
    with open('ini_file/new_massage.txt', 'r+', encoding='utf-8') as f:
        old_list = eval(f.read())
    if old_list.__len__() > 20:
        old_list = old_list[:17]

    new = []
    flag = 1
    num = 0
    while flag:
        nn, ck = get_ma_mun(text[num], keys=keys)
        if nn >= 1:
            # 关键词判定成功
            # 对有关键词的的电报进行筛选，看是否已经存在
            if text[num] not in old_list:  # 此条信息应被输出
                new.append(text[num])
                send_massage.send2wechat(message=f'所含关键词为：{"，".join(ck)} \n'+text[num],
                                         AgentId=ini_js['AgentId'],
                                         Secret=ini_js['Secret'],
                                         CompanyId=ini_js['CompanyId'])

            else:  # 此时可以认为不会有没有新的存在了，直接结束
                flag = 0
        num += 1
        if num == len(text):
            flag = 0

    with open('ini_file/new_massage.txt', 'w+', encoding='utf-8') as f:
        f.write(str(new+old_list))

    print(new)


if __name__ == '__main__':
    with open('ini_file/ini.json', 'r', encoding='utf-8') as f:
        ini_js = eval(f.read())
    for i in ini_js:
        print(i, ini_js[i])
    while 1:
        get_to_send(keys=ini_js['keywords'], ini_js=ini_js)
        time.sleep(int(ini_js['time_page']))



