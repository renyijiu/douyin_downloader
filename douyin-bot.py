# -*- coding: utf-8 -*-
import sys
import re
import random
import time
from multiprocessing import Queue, Process
from PIL import Image

from douyin import CrawlerScheduler

if sys.version_info.major != 3:
    print('Please run under Python3')
    exit(1)
try:
    from common import debug, config, screenshot
    from common.auto_adb import auto_adb
    from common import apiutil
    from common.compression import crop_image
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)

VERSION = "0.0.1"

# 我申请的 Key，建议自己申请一个，共用容易请求过于频繁导致接口报错
# 申请地址 http://ai.qq.com
AppID = '2119053868'
AppKey = 'pYGDDlXzkEIwvPH1'

DEBUG_SWITCH = True
FACE_PATH = 'tmp/face/'

adb = auto_adb()
adb.test_device()
config = config.open_accordant_config()

# 审美标准
BEAUTY_THRESHOLD = 85

# 最小年龄
GIRL_MIN_AGE = 18

# 识别性别: female, male
GENDER = 'female'

# 进程数
PROCESS = 5

def yes_or_no():
    """
    检查是否已经为启动程序做好了准备
    """
    while True:
        yes_or_no = str(input('请确保手机打开了 ADB 并连接了电脑，'
                              '然后打开手机软件，确定开始？[y/n]:'))
        if yes_or_no == 'y':
            break
        elif yes_or_no == 'n':
            print('谢谢使用')
            exit(0)
        else:
            print('请重新输入')


def _random_bias(num):
    """
    random bias
    :param num:
    :return:
    """
    return random.randint(-num, num)


def next_page():
    """
    翻到下一页
    :return:
    """

    time.sleep(1.5)
    cmd = 'shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=config['center_point']['x'],
        y1=config['center_point']['y'] + config['center_point']['ry'],
        x2=config['center_point']['x'],
        y2=config['center_point']['y'],
        duration=200
    )
    adb.run(cmd)


def follow_user():
    """
    关注用户
    :return:
    """
    cmd = 'shell input tap {x} {y}'.format(
        x=config['follow_bottom']['x'] + _random_bias(10),
        y=config['follow_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


def thumbs_up():
    """
    点赞
    :return:
    """
    cmd = 'shell input tap {x} {y}'.format(
        x=config['star_bottom']['x'] + _random_bias(10),
        y=config['star_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


def tap(x, y):
    """
    点击指定坐标位置

    :param x point
    :param y point
    :return 
    """

    cmd = 'shell input tap {x} {y}'.format(
        x=x + _random_bias(10),
        y=y + _random_bias(10)
    )
    adb.run(cmd)


def share_video():
    """点击分享视频按钮
    :return:
    """

    cmd = 'shell input tap {x} {y}'.format(
        x=config['share_bottom']['x'] + _random_bias(10),
        y=config['share_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)


def left_swipe():
    """向左滑动获取分享视频链接按钮
    :return:
    """

    # 多次滑动，确保能够正确得到按钮页面
    for _ in range(5):
        cmd = 'shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
            x1=config['left_swipe_point']['x'],
            y1=config['left_swipe_point']['y'],
            x2=config['left_swipe_point']['x'] - config['left_swipe_point']['rx'],
            y2=config['left_swipe_point']['y'],
            duration=200
        )
        adb.run(cmd)
        time.sleep(0.5)

def copy_link():
    """点击复制链接
    return: copy text
    """
    
    cmd = 'shell input tap {x} {y}'.format(
        x=config['copy_link_bottom']['x'],
        y=config['copy_link_bottom']['y']
    )
    adb.run(cmd)

    cmd_get_clipoard = 'shell am broadcast -a clipper.get'
    text = adb.run(cmd_get_clipoard)
    urls = re.findall(r'(http://v.douyin.com/\w+/)', text)
    return urls[0]


def main(queue):
    """
    main
    :return:
    """
    print('程序版本号：{}'.format(VERSION))
    print('激活窗口并按 CONTROL + C 组合键退出')
    debug.dump_device_info()
    screenshot.check_screenshot()

    while True:
        next_page()

        time.sleep(random.randint(1, 5))
        screenshot.pull_screenshot()

        crop_image('douyin.png', 
                    'optimized.png', 
                    config['crop_img']['x'], 
                    config['crop_img']['y'], 
                    config['crop_img']['width'],
                    config['crop_img']['height'])

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()

        ai_obj = apiutil.AiPlat(AppID, AppKey)
        rsp = ai_obj.face_detectface(image_data, 0)

        major_total = 0
        minor_total = 0
        if rsp['ret'] == 0:
            beauty = 0
            for face in rsp['data']['face_list']:
                msg_log = '[INFO] gender: {gender} age: {age} expression: {expression} beauty: {beauty}'.format(
                    gender=face['gender'],
                    age=face['age'],
                    expression=face['expression'],
                    beauty=face['beauty'],
                )
                print(msg_log)
                with Image.open("optimized.png") as im:
                    crop_img = im.crop((face['x'], face['y'], face['x']+face['width'], face['y']+face['height']))
                    crop_img.save(FACE_PATH + face['face_id'] + '.png')
                
                # 性别判断
                is_correct_gender = (face['gender'] < 50) if (GENDER == 'female') else (face['gender'] > 50)
                if face['beauty'] > beauty and is_correct_gender:
                    beauty = face['beauty']

                if face['age'] > GIRL_MIN_AGE:
                    major_total += 1
                else:
                    minor_total += 1

            # 发现符合要求的视频
            if beauty > BEAUTY_THRESHOLD and major_total > minor_total:
                msg = '发现漂亮妹子👀' if (GENDER == 'female')  else '发现帅气小哥👀'
                print(msg)
                thumbs_up()
                follow_user()
                share_video()
                left_swipe()
                video_url = copy_link()
                queue.put(video_url)
        else:
            print(rsp)
            continue


def download_videos(queue):
    """
    下载指定用户视频信息
    :return
    """

    while True:
        url = queue.get()
        if not url:
            continue
        print("get url from queue: " + url)
        CrawlerScheduler([url])
        time.sleep(10)


def download_processes(queue):
    """创建下载进程
    :return
    """

    for _ in range(PROCESS):
        proc = Process(target=download_videos, args=(queue,))
        proc.start()


if __name__ == '__main__':
    try:
        # yes_or_no()
        # main()
        queue = Queue()

        process = Process(target=main, args=(queue,))
        process.start()

        download_processes(queue)
        process.join()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('谢谢使用')
        exit(0)
