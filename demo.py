import json
import time
import requests
from loguru import logger

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
}


# 注册点字
def register_click():
    url = "https://passport.bilibili.com/x/passport-login/captcha"
    params = {
        "t": int(time.time() * 1000),
    }
    response = requests.get(url, headers=headers, params=params)
    challenge = response.json()["data"]["geetest"]["challenge"]
    gt = response.json()["data"]["geetest"]["gt"]
    token = response.json()["data"]["token"]
    # print('第一次请求：========>','challenge:',challenge,'gt:',gt)
    logger.info(f'获取验证码gt:{gt},challenge:{challenge},token:{token}')
    return token, gt, challenge


# 过验证码
def get_validate(gt,challenge):
    api_url = "http://127.0.0.1:6260/api/click"
    params = {
        "gt": gt,
        "challenge": challenge,
        # "ocr_url": "ocr_url",
        # "token": "token",
    }

    res = requests.get(api_url, params=params).json()['data']
    result = json.loads(res)['result']
    score = json.loads(res)['score']
    validate = json.loads(res)['validate']
    gt = json.loads(res)['gt']
    challenge = json.loads(res)['challenge']

    #print(result,score,validate,gt,challenge)
    return result,score,validate,gt,challenge


# 开始验证
def start():
    while True:
        token, gt, challenge = register_click()
        result,score,validate,gt,challenge = get_validate(gt, challenge)
        if result == "success":
            logger.success(f'点字验证成功========>result:{result},score:{score},validate:{validate},gt:{gt},challenge:{challenge},token:{token}')
            return token,validate,challenge
        else:
            logger.error(f'点字验证失败，重新验证')


# # 开始获取训练数据集，可删除
# def start_dataset():
#     while True:
#         token, gt, challenge = register_click()
#         result,score,validate,gt,challenge = get_validate(gt, challenge)
#         if result == "success":
#             logger.success(f'点字验证成功========>result:{result},score:{score},validate:{validate},gt:{gt},challenge:{challenge},token:{token}')
#             # return token,validate,challenge
#         else:
#             logger.error(f'点字验证失败，重新验证')

if __name__ == "__main__":
    token,validate,challenge = start()

