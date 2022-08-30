import time
import requests

# 填写对应的喵码
id = 'tyzTyr1'
# 填写喵提醒中，发送的消息，这里放上前面提到的图片外链
text = "告警图片：" + "http://rhba98p1b.hn-bkt.clouddn.com/sweet_sister.jpg"
ts = str(time.time())  # 时间戳
type = 'json'  # 返回内容格式
request_url = "http://miaotixing.com/trigger?"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'}

result = requests.post(request_url + "id=" + id + "&text=" + text + "&ts=" + ts + "&type=" + type,headers=headers)
# print(result)



