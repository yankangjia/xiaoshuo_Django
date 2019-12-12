import requests

#
# def send(mobile,captcha):
#     url = "http://v.juhe.cn/sms/send"
#     params = {
#         "mobile": mobile,
#         "tpl_id": "121674",
#         "tpl_value": "#code#="+captcha,
#         "key": "4f2dc49ce16b8538522f0f11fb6cd0a2"
#     }
#
#     # 账号失效无法发送
#     # response = requests.get(url,params=params)
#     # result = response.json()
#     # if result["error_code"] == 0:
#     #     return True
#     # else:
#     #     return False
#
#     # 模拟发送成功
#     return True




#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

client = AcsClient('LTAI4FdTV8hsuYYyTwT49Joj', 'kugY3ASwRhD9TwLDlenECl9wP893Xl', 'cn-hangzhou')

def send(mobile,captcha):
    return True     # 由于已欠费，不去真正发送验证码
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', mobile)
    request.add_query_param('SignName', "ykjzone")
    request.add_query_param('TemplateCode', "SMS_178451069")
    request.add_query_param('TemplateParam', '{"code":"%s"}'%captcha)

    response = client.do_action_with_exception(request)
    # response: {
    # 	"Message": "账户余额不足",
    # 	"RequestId": "3DC17A6C-8EFE-40A9-BA64-F12488912A30",
    # 	"Code": "isv.AMOUNT_NOT_ENOUGH"
    # }
    # print(str(response, encoding='utf-8'))
    if response['Code'] == 'ok':
        return True
    else:
        print(response['Message'])
        return False
