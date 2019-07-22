# -*- coding: utf-8 -*-

import os
import json
import re
import time
import getopt
import sys
from random import randrange
from requests_html import HTMLSession
from threading import Thread
from six.moves import queue as Queue

from local_file_adapter import LocalFileAdapter

MOBIE_HEADERS = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'cookie': '_ga=GA1.2.314211590.1562984162; tt_webid=6713786420811007495; _ba=BA0.2-20180421-5199e-J3qZPuhUDlMGLoEPpFeC; _gid=GA1.2.1866932789.1563518446'
}

# 线程数
THREADS = 10

# 重试次数
RETRY = 3

# 固定签名
FREEZE_SIGNATURE = None

def get_user_info(user_id):
    """获取用户的uid和dytk信息

    @param: user_id
    @return [uid, dytk]
    """

    base_url = 'https://www.iesdouyin.com/share/user/'
    session = HTMLSession()
    r = session.get(base_url + str(user_id), headers=MOBIE_HEADERS)
    uid = r.html.search('uid: "{uid}"')['uid']
    dytk = r.html.search("dytk: '{dytk}'")['dytk']
    return [uid, dytk]

def get_signature(user_id):
    """获取所需的签名信息
    
    @oaram: user_id
    @return: signature
    """
    
    session = HTMLSession()    
    signature_url = 'file://' + os.getcwd() + os.sep +'signature.html?user_id=' + str(user_id)
    session.mount("file://", LocalFileAdapter())
    r = session.get(signature_url, headers=MOBIE_HEADERS)
    r.html.render()
    sign = r.html.find('#signature', first=True)
    return sign.text

def get_list_by_uid(user_id, dytk, cursor=0):
    """获取用户视频列表信息

    @param: user_id
    @param: dytk
    @param: cursor,用于列表分页定位
    @return json
    """
    
    global FREEZE_SIGNATURE
    '''读取数据文件,若存在则直接返回'''
    file_result = load_from_json_file(user_id, cursor)
    if file_result:
        return file_result

    post_list_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/'
    '''获取签名'''
    signature = FREEZE_SIGNATURE if FREEZE_SIGNATURE else get_signature(user_id)
    headers = {
        **MOBIE_HEADERS,
        'x-requested-with': 'XMLHttpRequest',
        'accept': 'application/json'
    }
    params = {
        'user_id': user_id,
        'sec_uid': None,
        'count': 21,
        'max_cursor': cursor,
        'aid': 1128,
        '_signature': signature,
        'dytk': dytk
    }
    session = HTMLSession()
    while True:
        r = session.get(post_list_url, params=params, headers=headers)
        res_json = json.loads(r.html.text)
        if res_json.get('max_cursor', None):
            FREEZE_SIGNATURE = signature
            save_json_data(user_id, cursor, res_json)
            return res_json
        print("get empty list, " + str(res_json))
        time.sleep(1)
        print('retry...')
        
def save_user_video(url, user_id, video_id):
    """保存视频至当前video目录下对应的用户名目录

    @param: url
    @param: user_id
    @param: video_name
    @return None
    """
    
    if url is None:
        print('Error: can not get the download url!')
        return
    floder = os.path.join(os.getcwd(), 'video', user_id)
    if not os.path.exists(floder):
        try:
            os.mkdir(floder)
        except:
            pass
    video_path = os.path.join(floder, video_id + '.mp4')
    if not os.path.exists(video_path):
        url = custom_format_download_url(url)
        print('start to download the video, url: ' + url)

        retry_times = 0
        session = HTMLSession()
        while retry_times < RETRY:
            try:
                res = session.get(url, headers=MOBIE_HEADERS)
                if res.status_code == 200:
                    with open(video_path, "wb") as fp:
                        for chunk in res.iter_content(chunk_size=1024):
                            fp.write(chunk)
                    print('save video success, path: ' + video_path)
                    break
                else:  
                    raise Exception('request to download the video error, url' + url)
            except:
                pass 
            retry_times += 1
        else:
            try:
                os.remove(video_path)
            except OSError:
                pass
            print('Failed to download the video, url: ' + url)
    else:
        print("video already downloaded, skip!")
        pass

def custom_format_download_url(url):
    """自定义替换下载链接中的部分参数
    
    @param: url download_url
    @return url
    """

    url = url.replace('watermark=1', 'watermark=0')
    ratio = re.compile(r'ratio=(\d+)p')
    url = ratio.sub('ratio=720p', url)
    return url

def save_json_data(user_id, cursor, data):
    """保存用户视频列表的json数据

    @param: user_id
    @param: cursor
    @param: data json
    @return None
    """

    file_name = str(user_id) + '-' + str(cursor) + '.json'
    file_path = os.path.join(os.getcwd(), 'data', file_name)
    with open(file_path, 'w+', encoding='utf-8') as fb:
        json.dump(data, fb, ensure_ascii=False)
    print("list data save success!")

def load_from_json_file(user_id, cursor):
    """检查对应的data数据，查看是否已存在对应记录数据

    @param: user_id
    @param: cursor
    @return json
    """

    file_name = str(user_id) + '-' + str(cursor) + '.json'
    file_path = os.path.join(os.getcwd(), 'data', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = f.read()
        return json.loads(data)
    return None

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url, user_id, video_id = self.queue.get()
            save_user_video(url, user_id, video_id)
            self.queue.task_done()

class CrawlerScheduler(object):

    def __init__(self, items):
        self.user_ids = []
        for i in range(len(items)):
            url = self._get_real_user_link(items[i])
            if not url:
                continue
            number = re.findall(r'/share/user/(\d+)', url)
            if not len(number):
                continue
            self.user_ids.append(number[0])
        self.queue = Queue.Queue()
        self.scheduling()

    def scheduling(self):
        for _ in range(THREADS):
            worker = DownloadWorker(self.queue)
            worker.daemon = True
            worker.start()

        for user_id in self.user_ids:
            self.download_user_videos(user_id)
        self.queue.join()

    def download_user_videos(self, user_id):
        """下载用户所有视频

        @param: user_id
        @return
        """

        uid, dytk = get_user_info(user_id)
        self.push_download_job(uid, dytk)
        
    def push_download_job(self, user_id, dytk, cursor=0):
        """推送下载任务至队列

        @param: user_id
        @param: dytk
        @param: 分页游标
        @return
        """

        list_json = get_list_by_uid(user_id, dytk, cursor)
        for aweme in list_json.get('aweme_list', []):
            download_url_list = aweme.get('video', {}).get('download_addr', {}).get('url_list', [])
            video_id = aweme.get('statistics', {}).get('aweme_id', None)
            url = download_url_list[randrange(len(download_url_list))]
            self.queue.put((url, user_id, video_id))

        has_more = list_json.get('has_more', False)
        max_cursor = list_json.get('max_cursor', None)
        if has_more and max_cursor and (max_cursor != cursor):
            self.push_download_job(user_id, dytk, max_cursor)

    def _get_real_user_link(self, url):
        """从分享链接获取用户首页地址

        @param: url 抖音分享的用户首页链接
        @return: url 真实的用户首页链接
        """

        if url.find('v.douyin.com') < 0:
            return url
        session = HTMLSession()
        res = session.get(url, headers=MOBIE_HEADERS, allow_redirects=False)
        if res.status_code == 302:
            user_url = res.headers['Location']
            return user_url
        return None


def usage():
    print("1. Please make sure folder data/ and video/ is exist under this same diectory.\n"
          "2. Please create file share-url.txt under this same directory.\n"
          "3. In share-url.txt, you can specify one amemv share page url one line. Accept multiple lines of text\n"
          "4. Save the file and retry.\n"
          "5. Or use command line options:\nSample: python douyin.py --urls url1,url2\n\n")
    print("1. 请确保在当前目录下，存在data和video文件夹。\n"
          "2. 请确保当前目录下存在share-url.txt文件。\n"
          "3. 请在文件中指定抖音分享页面URL，一行一个链接，支持多行.\n"
          "4. 保存文件并重试.\n"
          "5. 或者直接使用命令行参数指定链接\n例子: python douyin.py --urls url1,url2")

def get_file_content(filename):
    if os.path.exists(filename):
        return parse_sites(filename)
    else:
        usage()
        sys.exit(1)

def parse_sites(filename):
    urls = []
    with open(filename, 'r') as f:
        for line in f:
            url = line.strip()
            if url:
                urls.append(url)
    return urls

if __name__ == "__main__": 
    content, opts, args = None, None, []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:f:", ["help", "urls=", "filename="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-u', '--urls'):
            content = arg.split(',')
        elif opt in ('-f', '--filename'):
            content = get_file_content(arg)
        elif opt in ('-h', '--help'):
            usage()
            sys.exit()
    
    if not content:
        content = get_file_content('share-url.txt')
    
    if len(content) < 1 or content[0] == '':
        usage()
        sys.exit(1)

    CrawlerScheduler(content)