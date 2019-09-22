import json

import requests


def verifyHttp(api_username, api_password, file_name, api_post_url):
    """

    :param api_username: 账号
    :param api_password: 密码
    :param file_name: 识别文件路径
    :param api_post_url: api接口地址
    :param yzm_min: 识别结果最小长度值 (空)
    :param yzm_max: 识别结果最大长度值 (空)
    :param yzm_type: 识别类型 (空)
    :param tools_token: 软件token(空)
    :return:
    """

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
        # 'Content-Type': 'multipart/form-data; boundary=---------------------------227973204131376',
        'Connection': 'keep-alive',
        'Host': 'v1-http-api.jsdama.com',
        'Upgrade-Insecure-Requests': '1'
    }

    files = {
        'upload': (file_name, open(file_name, 'rb'), 'image/png')
    }

    data = {
        'user_name': api_username,
        'user_pw': api_password
    }

    s = requests.session()

    r = s.post(api_post_url, headers=headers, data=data, files=files, verify=False)

    return r.text


def verifyfile(file_name):
    return verifyHttp(api_username="yqsy021", api_password="XK8mqwS6R.C25t2",
                      file_name=file_name,
                      api_post_url="http://v1-http-api.jsdama.com/api.php?mod=php&act=upload")


def main():
    # t = verifyfile("D:/win/studio/dxf/picture/yanzheng/yanzheng1.png")

    # print(t)

    t = '{"result":true,"data":{"id":34082088072,"val":"TKBH"}}'

    loaded_json = json.loads(t)

    print(loaded_json["result"])


if __name__ == '__main__':
    main()
