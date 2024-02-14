import json
import re
import time
import execjs, requests
from pathlib import Path
import ddddocr
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from loguru import logger
import io, ddddocr, random, rsa, hashlib
from gsxt_val_238 import get_val
import base64

class Geetest(object):
    def __init__(self,ocr_url,token):
        self.OCR_URL = ocr_url
        self.TOKEN = token

        # 初始化目标检测和OCR模型
        self.det = ddddocr.DdddOcr(det=True)  # 用于检测
        self.ocr = ddddocr.DdddOcr(beta=True)  # 用于OCR
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

    # # 注册点字
    # def register_click(self):
    #
    #     url = "https://passport.bilibili.com/x/passport-login/captcha"
    #     params = {
    #         "t": int(time.time() * 1000),
    #     }
    #     response = requests.get(url, headers=self.headers, params=params)
    #     challenge = response.json()["data"]["geetest"]["challenge"]
    #     gt = response.json()["data"]["geetest"]["gt"]
    #     token = response.json()["data"]["token"]
    #     # print('第一次请求：========>','challenge:',challenge,'gt:',gt)
    #     logger.info(f'\n第一次请求========>gt:{gt},challenge:{challenge},token:{token}')
    #     return token, gt, challenge

    def get_php(self, gt, challenge):
        url = "https://api.geetest.com/get.php"

        params = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            # "w": "5muM2kn7Svi7zzGDxxypVT6XzuttqbrJWA4z4i1bMDYasNZnNQA(1vWHEjH)sh0Hsj2EXxDIDFxZxv2jFh1y(SfgWZw3JJymYtUOK3wl7NKV4icZZR1FtiGfYwn64Zhh0h6IVnHARVbsZmzYVmCZ6SAzMdvXspxPNKP0voSPr9qUTd8WSIQzOBIacy0mqAtaCRiwws5f3FIPhD1JpQvLZaBlYEOfmy(8buQ7I(NjffOZ7PKtjGpW9xqTX4DxAjxtWgd5dXHVexs5d7OQHySL8H4RuyUucsWnoU9BwBrAqaNDsrs5ZYPSmfUo2C(R1J3Ku1jwQKo26Z7(81Uahw5Hpi1w4DREFkJI50US0iW7j3ZEBhpOpdwNu7oQcIzx(WvjgzclXXfabdIWf6A0pgTpv6of9g(Kk77TqtlTt5oMMUi4PcYjrjk4oojAdrLasONqifhXMDNJ)I7ucYuiu)J8cx1nSMY0J4Dy200LSf710oCpfur9F)6cbHRcigNGeO2eK1LOdV9BzQtbcqEE(Bm2niqpPYrapqtxW13DdLDfjLl6FKrg24TSoWix0mwtc3wBf62hYmONpztTo8SrMwKAMbR3cQVZVw32rHpaAqdXSS3NSOcrs)Jkwc1DUiu(AR68LCXEmRPbSM4Rh1g1VuXLieL4jccfzegluBHRGyl6u(oVPKynpvibAskHYJwapp9Jc2FMQXlQuPS6e)oP8vOEIqj(EfeBFF)YWOtiLVZLttLO1h3iXsuyU4Sbb)(938L)5hjZkL4cRAEObKaYlkEy04jTFOWmb17IbvcYg)Ga3heAGTyc1(eosFL5W1H5np)jN09xRm28JYVxOaPAq5R7QXOLK8KmGlQZoWHraYQSMJCcA8(UlujsePkaJRtJHmLeAXbk82JSOwrS0ObVuAPQi)iLS7AF5M2G66Vhjhs6oPsazHmc850siVZLvppvNXB6nQdVYO4aLqtvOHeX3XgBz)2zhEHZh6E8214GcD25SYKtFhVS5i6D3NZGjo7B9rmmtG)TdgSQFAiqfPBmXkL4fLi7d2XzCUplb)KhquezjuK(pJwuas5xdZoCxCGQDsL2etzx5FuvjO6nFGsXzPOfEujC8IQxD3yDJMzA0HEpM76NmgLScs5bckLjgYjcfAClqLXF8Hqub8W8YQHynFx1Tp7pP1HslfI8W)l2ok8KAvuFkvUqJPFpfzFZpP4OyjsfKHo)7S5Lihj7V9I6xHOA8SLsUcLfAFUDLhyIpM9i8397DYzNRe)25ucxK2pzcF4qbdQ49sX6RAbQgp68FhTb4dbG(yh3ONgqQFQOS4RmfMo5OrVX1J1QCiTZ7FqJH9aLiiucWjeXBz1XkaWudjWGR5s18ly1VMmJ1gv02aI)4htdBJuXs7rLf9B)lHvtJzyQypvJg8jsi8)jXOYIkt1(EGsV3A7iVMtO)tIu5sU5MHugkj5drWVyatC0HKGCpuRRNjyAlsP)HWHgDOe4UsQdXDp84vbf2AUzeSOPSXa6fnjuK8nnQsPZqcf8cJFtox2QFVL2JAut(9SPCuYE9RTKcqLJeY(dalbbZlToRXvrc6ImJc8iVTKCJ6Fk9GxgGAwT1EZOU4QpnpnI01ednFLQSjGWglhnxuaOn9rg2oSYcCFhWgrYwqPf(njEwZqms0YnqYsAe(LN)bcCkBmmBiUljrsguw5ZXjiBcreQxUp4VHmlTFxjHlJwZi9qFJaIU5Bi9v2PDVIDNn6hgt)soxYa52aKDkeGod5w5Ya3AfmTeXQM2QxMwkXuukAFGcqnGXEUlJfGkTPBPYrIqV1hE5F36hQVNjHuhnnTAzmkSueqUCSBCIcFCe4J4)K9)pRqUIuhtVeflXmG1qgudRofpm(VAgG5RsdMxEhpQnMg9sHaHDyUEaZIy0(BruLLbUhNkLHQ0kQ1Cy9mzQO3w4YR2MkRLtUuB8MT(xLRB(bVkVw9FXWP0LlJ5JLTQz8CvBnAG7iv6JuOWDNYW58NJnYHERMIPPCNIfo0bUEMflzlLFSUiaiDCxGpwi6X9lmzljrfyl0BRCti1zv4ewRW(Q6bgzZ4FWD9Q9ePkgD)AQhK0f6HRGvsyoqlQ7UaEHbG1U1sAzJbQTs5s9efEl4tMzrZklM0GEaGuoL7QV5JmBvt8S6Ph8XxiCg6lIbNafnMfdOELyRcSBcUInNAiiNHuDn5bHRtW)1AK)9paViMlzP4oymvrED6XnGH7Ep9932mSyTTh3BiE4zhLt0(rEM(0XXhmmIG8)MwtSv38FQ3Y67dwT5FcUBCpC80zO1e9NF2wcQWjegHHWhbdaiAAsFATvqDh4z)1JQa((4WlejcrV)SvfcNLDRFVngdy6z0GNpyEcOmLKwRn7SNiaK)rHS0ymVRfgJUzDRtqskDJBZdhvL7ZnhxvQI.333fb38885e00d146b510c454db2cedb23eb32726cf1d6408e59cd1d730c91885d24164cf4eb785165a1a38fd9df94c98756486393528c131908fc9ac532c48c0f310e57be79f8522fe91334903fdeadbdcf00a63f986b242649c8707a14a0ad4909c91e53faaaf12ff71d57ecaad2ffeabeb801265f037db748b24d1474fd4c",
            "callback": "geetest_" + str(int(time.time() * 1000))
        }
        response = requests.get(url, headers=self.headers, params=params)

        res = re.findall(r'geetest_\d*[(](.*)[)]', response.text)[0]
        c = json.loads(res)['data']['c']
        s = json.loads(res)['data']['s']

        # print('\n第二次请求========>', 'c的值:',c,'s的值：',s)
        logger.info(f'第二次请求========>c的值:{c} s的值{s}')

        return c, s

    def ajax_php(self, gt, challenge):
        url = "https://api.geetest.com/ajax.php"
        params = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            # "w": "",
            "callback": "geetest_" + str(int(time.time() * 1000))
        }
        # print(params)
        response = requests.get(url, headers=self.headers, params=params)

        # print('\n第三次请求========>', '请求验证类型:',response.text)
        logger.info(f'第三次请求========>请求验证类型:{response.text}')

    def get_click(self, gt, challenge):
        url = "https://api.geetest.com/get.php"
        params = {
            "is_next": "true",
            "type": "click",
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "https": "false",
            "protocol": "https://",
            "offline": "false",
            "product": "embed",
            "api_server": "api.geetest.com",
            "isPC": "true",
            "autoReset": "true",
            "width": "100%",
            "callback": "geetest_" + str(int(time.time() * 1000))
        }
        response = requests.get(url, headers=self.headers, params=params)
        try:
            # print(response.text)
            res = re.findall(r'geetest_\d*[(](.*)[)]', response.text)[0]
            # challenge = json.loads(res)['challenge']
            pic = json.loads(res)['data']['pic']
            c = json.dumps(json.loads(res)['data']['c'], ensure_ascii=False)
            s = json.loads(res)['data']['s']
            code_nums = json.loads(res)['data']['num']
            # 请求图片并保存
            img_url = 'http://static.geetest.com%s?challenge=%s' % (pic, challenge)
            # print(img_url)
            image = requests.get(img_url, headers=self.headers)
            bg_path = 'click.jpg'
            with open(bg_path, 'wb') as f:
                f.write(image.content)
            return c,s,pic
        except:
            logger.error('第四次请求========>请求失败,gt和challenge值已失效')
            return None, None, None

    # 验证点字信息
    def get_validate(self, model, gt, challenge, c, s, pic):
        url = "https://api.geetest.com/ajax.php"

        # 根据模式选择验证方法
        if model == "ddddocr":
            data = self.click_chinese("click.jpg")
        else:
            data = self.ocr_validate("click.jpg")

        # 检测识别是否成功
        if data is None:
            logger.error('识别点字失败')
            # print("识别失败")
            return None, None, None

        # print("识别成功")
        logger.info('识别点字成功')
        # print(f'极验文字点选识别结果： {data}')
        logger.info(f'极验文字点选识别结果： {data}')

        points = [str(int(round(v.get('x') / 344 * 10000, 0))) + '_' + str(
            int(round(v.get('y') / 344 * 10000, 0))) for v in data.values()]
        points = ','.join(points)
        w = get_val(points, challenge, gt, pic, c, s)

        time.sleep(random.uniform(2, 3))
        params = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "$_BCX": "0",
            "client_type": "web",
            "w": w,
            "callback": "geetest_" + str(int(time.time() * 1000))
        }

        # response = requests.get(url, headers=self.headers, params=params)
        response = requests.get(url, headers=self.headers, params=params)
        # print(response.text)
        try:
            res = re.findall(r'geetest_\d*[(](.*)[)]', response.text)[0]
            data = json.loads(res)

            result = data.get('data', {}).get('result')
            validate = data.get('data', {}).get('validate')
            score = data.get('data', {}).get('score')

            # print(f"Status: {result}, Validate: {validate}, Score: {score}")

            if result == "success":
                logger.success(f"验证点字成功: Status: {result}, Validate: {validate}, Score: {score}")
                return result, validate, score
            else:
                logger.error(f'验证点字失败: {response.text}')
                return None, None, None
        except:
            logger.error(f'验证点字失败: {response.text}')
            return None, None, None

    # 先检测每个字符的位置，再识别
    def git_dict(self, image_file):
        # 读取图像
        with open(image_file, 'rb') as f:
            image = f.read()
        # 进行目标检测，找到图像中的文字区域
        poses = self.det.detection(image)
        # 使用OpenCV读取同一图像，以便后续处理和展示
        im = cv2.imread(image_file)
        # 转换为Pillow图像以便绘制中文
        im_pil = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(im_pil)
        # 为了支持中文，你需要指定一个包含中文的字体文件
        # 请确保这个路径是正确的，并且字体文件支持你需要显示的文字
        font_path = "Alibaba-PuHuiTi-Regular.ttf"  # 示例字体路径，需要替换
        font = ImageFont.truetype(font_path, 30)  # 字体大小
        # 初始化保存识别结果的字典
        dict = {}

        # 遍历检测到的文字区域
        for box in poses:
            x1, y1, x2, y2 = map(int, box)
            # 截取每个文字区域的图像
            roi = im[y1:y2, x1:x2]
            # 将OpenCV图像转换为PIL图像，然后转换为字节流，以便ddddocr进行处理
            roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            roi_bytes = io.BytesIO()
            roi_pil.save(roi_bytes, format='JPEG')
            # 对每个文字区域进行OCR识别
            text = self.ocr.classification(roi_bytes.getvalue())
            # 计算文字中心坐标
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            # 保存识别结果到字典
            dict[text] = {"x": center_x, "y": center_y}

            # 输出识别的文字和对应的坐标
            # print(f'Text: "{text}" at position: ({x1}, {y1}, {x2}, {y2})')

            # 在原图上标注文字区域
            cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=1)
            # 使用Pillow绘制矩形框和文字
            draw.rectangle([x1, y1, x2, y2], outline="green", width=2)
            draw.text((x1, y1 - 30), text, fill="red", font=font)

        # 将Pillow图像转换回OpenCV图像
        im = cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)

        # 保存标注后的图像
        cv2.imwrite("annotated_" + image_file, im)
        # print(dict)
        return dict

    # 识别验证码
    def click_chinese(self, image_file):
        # 加载原始图像
        original_img = cv2.imread(image_file)

        # 分割图像
        verification_img = original_img[0:344, 0:344]  # 获取verification.jpg区域
        require_img = original_img[344:384, 0:150]  # 从图像右侧截取150像素宽度的区域  # 获取require.jpg区域

        # 保存分割后的图像
        cv2.imwrite("verification.jpg", verification_img)
        cv2.imwrite("require.jpg", require_img)

        # 初始化目标检测和OCR模型
        det = ddddocr.DdddOcr(det=True)  # 用于检测
        ocr = ddddocr.DdddOcr(beta=True)  # 用于OCR

        verification_dict = self.git_dict("verification.jpg")
        require_dict = self.git_dict("require.jpg")
        # require_dict根据x坐标的大小排序，提取键形成新的列表
        require_list = sorted(require_dict, key=lambda k: require_dict[k]['x'])
        sorted_by_require_dict = {}
        # 验证并排序verification_dict
        try:
            # 检查verification_dict中是否包含require_list的所有元素
            if not all(item in verification_dict for item in require_list):
                raise ValueError("verification_dict does not contain all required keys.")

            # 根据require_list的顺序重组字典
            for idx, key in enumerate(require_list, start=1):
                if key in verification_dict:
                    sorted_by_require_dict[str(idx)] = verification_dict[key]

            # print(sorted_by_require_dict)
            return sorted_by_require_dict
        except ValueError as e:
            return None

    # 打码验证点字信息
    def ocr_validate(self, image_file):
        # 打开图片文件（以二进制模式）
        with open(image_file, "rb") as image_file:
            image_data = image_file.read()
            # 将图片数据转换为Base64编码的字符串
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        params = {
            "image": image_base64,
            "extra": "click",
            "token": self.TOKEN,
            "type": "30103"
        }
        try:
            response = requests.post(self.OCR_URL, data=params).json()
            # print(response)
            msg = str(response['msg'])
            code = str(response['code'])
            result = str(response['data']['data'])

            # 识别成功
            if code == "10000":
                # 分割字符串获取坐标对
                coordinates = result.split("|")
                # 初始化结果字典
                result_dict = {}
                # 遍历坐标对，分割每对坐标为x和y，并添加到结果字典
                for i, coord in enumerate(coordinates, start=1):
                    x, y = coord.split(",")
                    result_dict[str(i)] = {"x": int(x), "y": int(y)}
                # 打印结果字典
                # print(result_dict)
                return result_dict
            else:
                logger.info(f'ocr验证点字失败：{msg}')
                return
        except:
            logger.info('ocr验证点字失败：网络错误')
            return None

    def run(self,model,gt,challenge):
        # token, gt, challenge = self.register_click()
        # gt = '3378262dc41a29fef92707dc5709d53d'
        c, s = self.get_php(gt, challenge)
        self.ajax_php(gt, challenge)
        # 返回challenge和s参数
        c, s, pic = self.get_click(gt, challenge)

        # 验证滑块信息
        result, validate, score = self.get_validate(model, gt, challenge, c, s, pic)

        # 创建包含所需字段的字典
        data = {
            "result": result,
            "score": score,
            # "token": token,
            "validate": validate,
            "gt": gt,
            "challenge": challenge
        }
        json_str = json.dumps(data)
        return json_str



    # # 以下是获取训练用数据代码，可以删除
    # def get_data_click(self, gt, challenge):
    #     url = "https://api.geetest.com/get.php"
    #     params = {
    #         "is_next": "true",
    #         "type": "click",
    #         "gt": gt,
    #         "challenge": challenge,
    #         "lang": "zh-cn",
    #         "https": "false",
    #         "protocol": "https://",
    #         "offline": "false",
    #         "product": "embed",
    #         "api_server": "api.geetest.com",
    #         "isPC": "true",
    #         "autoReset": "true",
    #         "width": "100%",
    #         "callback": "geetest_" + str(int(time.time() * 1000))
    #     }
    #     response = requests.get(url, headers=self.headers, params=params)
    #     try:
    #         # print(response.text)
    #         res = re.findall(r'geetest_\d*[(](.*)[)]', response.text)[0]
    #         # challenge = json.loads(res)['challenge']
    #         pic = json.loads(res)['data']['pic']
    #         c = json.dumps(json.loads(res)['data']['c'], ensure_ascii=False)
    #         s = json.loads(res)['data']['s']
    #         code_nums = json.loads(res)['data']['num']
    #         # 请求图片并保存
    #         img_url = 'http://static.geetest.com%s?challenge=%s' % (pic, challenge)
    #         # print(img_url)
    #         image = requests.get(img_url, headers=self.headers)
    #         bg_path = 'data/'+challenge+'.jpg'
    #         with open(bg_path, 'wb') as f:
    #             f.write(image.content)
    #         return c,s,pic
    #     except:
    #         logger.error('第四次请求========>请求失败,gt和challenge值已失效')
    #         return None, None, None
    #
    #
    # def run(self,gt,challenge):
    #
    #     c, s = self.get_php(gt, challenge)
    #     self.ajax_php(gt, challenge)
    #     # 返回challenge和s参数
    #     c, s, pic = self.get_data_click(gt, challenge)
    #
    #     # 创建包含所需字段的字典
    #     data = {
    #         "result": "success",
    #         "score": "100",
    #         # "token": token,
    #         "validate": "validate",
    #         "gt": gt,
    #         "challenge": challenge
    #     }
    #     json_str = json.dumps(data)
    #     return json_str

if __name__ == '__main__':
    GEET_click = Geetest("ocr_url", "token")
    GEET_click.run("ddddocr","ac597a4506fee079629df5d8b66dd4fe","ede1125c3884ce780707a6ebc06b8ff1")
