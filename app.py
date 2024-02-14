from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from geet_click3 import Geetest
import re

app = Flask(__name__)
executor = ThreadPoolExecutor(10)
# 全局变量来存储validation_code
validation_code = None


# 获取gt和challenge
@app.route("/api/click", methods=['GET', 'POST'])
def index():
    # 检查请求中是否包含gt,challenge参数
    gt = request.args.get('gt')
    challenge = request.args.get('challenge')

    ocr_url = request.args.get('ocr_url')
    token = request.args.get('token')

    # print(challenge)
    if not challenge or not gt:
        # 如果没有gt,challenge参数，则返回错误JSON响应
        return jsonify(error='请求参数错误'), 400
    if len(challenge) != 32:
        return jsonify(error='请求参数错误'), 400

    # 调用ddddocr
    if ocr_url is None or token is None:
        model = "ddddocr"
    else:
        model = "ocr"

    # 在这里处理包含challenge参数的异步请求
    future = executor.submit(get_click, ocr_url, token, model, gt, challenge)
    return future.result()



# 点字验证函数
def get_click(ocr_url, token, model, gt, challenge):
    click = Geetest(ocr_url, token)
    res = click.run(model, gt, challenge)
    return {"data": res}


# 接受手机发来的验证码（task APP）
@app.route("/api/sms", methods=['POST'])
def handle_sms():
    # 确保请求是JSON格式
    if request.is_json:
        # 获取解析后的JSON数据
        data = request.json
        # 从数据中提取SMSRB的值
        smsrb = data.get('SMSRB', '')  # 使用get方法安全访问键值，如果SMSRB不存在，返回空字符串

        # 使用正则表达式匹配数字序列
        match = re.search(r'\d+', smsrb)
        if match:
            # 如果找到匹配，提取验证码，保存到全局变量中
            global validation_code
            validation_code = match.group()
            # print("Validation code:", validation_code)

            # 在这里处理包含challenge参数的异步请求
            executor.submit(validation_code)

        return jsonify(status='OK'), 200
    else:
        return jsonify(error='JSON数据无效，请检查是否包含短信内容SMSRB'), 400


# 获取短信验证码
@app.route("/api/get_validation_code", methods=['GET'])
def get_validation_code():
    return jsonify(validation_code=validation_code), 200


# 重置短信验证码
@app.route("/api/reset_validation_code", methods=['GET'])
def set_validation_code():
    global validation_code
    validation_code = None
    return jsonify(status='OK'), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6260)
