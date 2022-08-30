import cv2
import mediapipe as mp
import time
import math
from qiniu import Auth, put_file
from qiniu import CdnManager
import requests

# 配置七牛云信息
access_key = "89H2_awA7F-IxHhwwLx-RCCu_YurvRm8yRHnqul7"
secret_key = "SPEaKaJ9uEe7DIVRbL--1RT6rNNF1vxwyiPWcdNM"
bucket_name = "person-fall-detection"
bucket_url = "rhba98p1b.hn-bkt.clouddn.com"

q = Auth(access_key, secret_key)
cdn_manager = CdnManager(q)


mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True,model_complexity=1,smooth_landmarks=True,
                    min_detection_confidence=0.5,min_tracking_confidence=0.5)
drawing = mp.solutions.drawing_utils

id = 'tyzTyr1'

# 将本地图片上传到七牛云中
def upload_img(bucket_name, file_name, file_path):
    # generate token
    token = q.upload_token(bucket_name, file_name)
    put_file(token, file_name, file_path)

# 获得七牛云服务器上file_name的图片外链
def get_img_url(bucket_url, file_name):
    img_url = 'http://%s/%s' % (bucket_url, file_name)
    return img_url


def upload_qiniu():
    # 需要上传到七牛云上面的图片的路径
    image_up_name = "detect_image.jpg"
    # 上传到七牛云后，保存成的图片名称
    image_qiniu_name = "detect_image.jpg"
    # 将图片上传到七牛云,并保存成image_qiniu_name的名称
    upload_img(bucket_name, image_qiniu_name, image_up_name)
    # 取出和image_qiniu_name一样名称图片的url
    url_receive = get_img_url(bucket_url, image_qiniu_name)
    print(url_receive)

    # 需要刷新的文件链接,由于不同时间段上传的图片有缓存，因此需要CDN清除缓存，
    urls = [url_receive]
    # URL刷新缓存链接,一天有500次的刷新缓存机会
    refresh_url_result = cdn_manager.refresh_urls(urls)
    return url_receive


def main():
    cap = cv2.VideoCapture('test.mp4')
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 指定视频编码格式
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频的fps
    out_path = "test_result.mp4"
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取视频的宽高
    out = cv2.VideoWriter(out_path, fourcc, fps, frame_size)

    succes ,image = cap.read()
    h = image.shape[0]
    while cap.isOpened():
        succes, img = cap.read()
        if succes:
            results = pose.process(img)
            key_point_y = []
            if results.pose_landmarks:
                drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                for i in range(33):
                    cy = int(results.pose_landmarks.landmark[i].y * h)
                    key_point_y.append(cy)
                left_shoulder_y = key_point_y[11]
                right_shoulder_y = key_point_y[12]
                shoulder_y = (left_shoulder_y + right_shoulder_y) // 2
                left_ankle = key_point_y[27]
                right_ankle = key_point_y[28]
                ankle_y = (left_ankle + right_ankle) // 2
                value = ankle_y - shoulder_y
                if value < 0:
                    print("有人摔倒")
                    cv2.imwrite("detect_image.jpg", img)
                    url_receive = upload_qiniu()
                    text = "告警图片：" + url_receive
                    ts = str(time.time())  # 时间戳
                    type = 'json'  # 返回内容格式
                    request_url = "http://miaotixing.com/trigger?"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'}

                    result = requests.post(request_url + "id=" + id + "&text=" + text + "&ts=" + ts + "&type=" + type,
                                           headers=headers)

            out.write(img)  # 保存检测结果
            cv2.imshow("Image", img)
            cv2.waitKey(1)
        else:
            break


if __name__ == "__main__":
    main()

















