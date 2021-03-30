# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/3/25 19:17
# Description:

import os
import json
import time
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
"""
python发消息给微信
"""


def send2wechat(AgentId, Secret, CompanyId, message):
    """
    :param AgentId: 应用ID
    :param Secret: 应用Secret
    :param CompanyId: 企业ID
    """
    # 通行密钥
    ACCESS_TOKEN = None
    # 如果本地保存的有通行密钥且时间不超过两小时，就用本地的通行密钥
    if os.path.exists('ACCESS_TOKEN.txt'):
        txt_last_edit_time = os.stat('ACCESS_TOKEN.txt').st_mtime
        now_time = time.time()
        print('ACCESS_TOKEN_time:', int(now_time - txt_last_edit_time))
        if now_time - txt_last_edit_time < 7200:  # 官方说通行密钥2小时刷新
            with open('ACCESS_TOKEN.txt', 'r') as f:
                ACCESS_TOKEN = f.read()
                # print(ACCESS_TOKEN)
    # 如果不存在本地通行密钥，通过企业ID和应用Secret获取
    if not ACCESS_TOKEN:
        r = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CompanyId}&corpsecret={Secret}'
        ).json()
        ACCESS_TOKEN = r["access_token"]
        # print(ACCESS_TOKEN)
        # 保存通行密钥到本地ACCESS_TOKEN.txt
        with open('ACCESS_TOKEN.txt', 'w', encoding='utf-8') as f:
            f.write(ACCESS_TOKEN)
    # 要发送的信息格式
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": f"{AgentId}",
        "text": {
            "content": f"{message}"
        }
    }
    # 字典转成json，不然会报错
    data = json.dumps(data)
    # 发送消息
    r = requests.post(
        f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}',
        data=data)
    # print(r.json())


def get_Visib(iata):
    headers = {
        'Host': 'adsbapi.variflight.com',
        'sec-ch-ua':
        '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'Origin': 'https://flightadsb.variflight.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://flightadsb.variflight.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # params = (
    #     ('lang', 'zh_CN'),
    #     ('iata', 'WMT'),
    # )
    params = (
        ('lang', 'zh_CN'),
        ('iata', iata),
    )

    # 请求飞常准接口
    response = requests.post(
        'https://adsbapi.variflight.com/adsb/airport/api/fweather',
        headers=headers,
        params=params)
    a = json.loads(response.text)
    # print(response.text)
    return (a["current"]["Visib"])
    # return (response.text)


def start():
    threshold = 10000
    WMT_Visib = get_Visib("WMT")
    time.sleep(1)
    SHA_Visib = get_Visib("SHA")
    time.sleep(1)
    LPF_Visib = get_Visib("LPF")
    time.sleep(1)
    LLB_Visib = get_Visib("LLB")
    time.sleep(1)
    CTU_Visib = get_Visib("CTU")
    # 应用ID
    AgentId_ = '1000002'
    # 应用Secret
    Secret_ = '168O38wlLevOWinTbDzObQha_Sgel7rRJmkO0JLvGHw'
    # 企业ID
    CompanyId_ = 'ww37999dd7e3088b5d'
    # 发送的消息
    message_ = "当前能见度:\n茅台：\t" + WMT_Visib + "\n虹桥：\t" + SHA_Visib + "\n六盘水: \t" + LPF_Visib + "\n荔波：\t" + LLB_Visib + "\n成都：\t" + CTU_Visib
    # message_ = "test"
    # return message_
    if int(WMT_Visib) <= threshold or int(SHA_Visib) <= threshold or int(
            LPF_Visib) <= threshold or int(LLB_Visib) <= threshold or int(
                CTU_Visib) <= threshold:
        send2wechat(AgentId_, Secret_, CompanyId_, message_)
    else:
        print("目前所有机场情况良好")


def notice():
    threshold = 2000
    airport_dict = {
        "茅台": "WMT",
        "虹桥": "SHA",
        "六盘水": "LPF",
        "荔波": "LLB",
        "成都": "CTU",
        "铜仁": "TEN",
        "毕节": "BFJ",
        "河池": "HCJ"
    }
    Visib_dict = {}
    for key, value in airport_dict.items():
        time.sleep(3)
        Visib = get_Visib(value)
        if int(Visib) <= threshold:
            Visib_dict[key] = Visib
    if Visib_dict != None:
        print(str(Visib_dict))
        requests.post('https://api.day.app/McaXaFtnXqWuGeo7Tig9xC/机场能见度监控/' +
                      str(Visib_dict))  # 孙浩
        requests.post('https://api.day.app/7t4rX5X2UkqDkrGRtgp5WK/机场能见度监控：' +
                      str(Visib_dict))  # 薛士翔
    else:
        print("目前所有机场情况良好")


if __name__ == '__main__':
    print("----------------定时任务运行中-----------------------")
    scheduler = BlockingScheduler()
    scheduler.add_job(notice, 'cron', hour='8-23', minute='4')
    scheduler.start()
