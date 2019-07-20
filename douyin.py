# -*- coding: utf-8 -*-

import os
import json
import re
import time
from random import randrange
from requests_html import HTMLSession
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

# 获取用户首页信息
user_info_url = 'https://www.iesdouyin.com/share/user/'
# 获取用户视频列表信息
post_list_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/'
# 固定签名
freeze_signature = None
# 构建请求
session = HTMLSession()

def get_user_info(user_id):
    """获取用户的uid和dytk信息

    @param: user_id
    @return [uid, dytk]
    """

    r = session.get(user_info_url + str(user_id), headers=MOBIE_HEADERS)
    uid = r.html.search('uid: "{uid}"')['uid']
    dytk = r.html.search("dytk: '{dytk}'")['dytk']
    return [uid, dytk]

def get_signature(user_id):
    """获取所需的签名信息
    
    @oaram: user_id
    @return: signature
    """
    
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
    
    global freeze_signature
    '''读取数据文件'''
    file_result = load_from_json_file(user_id, cursor)
    if file_result:
        return file_result
    
    '''获取签名'''
    signature = freeze_signature if freeze_signature else get_signature(user_id)
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
    while True:
        r = session.get(post_list_url, params=params, headers=headers)
        res_json = json.loads(r.html.text)
        if res_json.get('max_cursor', None):
            freeze_signature = signature
            save_json_data(user_id, cursor, res_json)
            return res_json
        print("get empty list, " + str(res_json))
        time.sleep(randrange(1, 5))
        print('retry...')

def download_video(user_id, dytk, cursor=0):
    """下载用户的所有视频

    @param: user_id
    @param: dytk
    @param: cursor 分页游标
    @return None
    """

    list_json = get_list_by_uid(user_id, dytk, cursor)
    for aweme in list_json.get('aweme_list', []):
        download_url_list = aweme.get('video', {}).get('download_addr', {}).get('url_list', [])
        video_id = aweme.get('statistics', {}).get('aweme_id', None)
        save_video(download_url_list, user_id, video_id)

    has_more = list_json.get('has_more', False)
    max_cursor = list_json.get('max_cursor', None)
    if has_more and max_cursor and (max_cursor != cursor):
        download_video(user_id, dytk, max_cursor)
        
def save_video(url_list, user_id, video_name):
    """保存视频至当前video目录下对应的用户名目录

    @param: url_list
    @param: user_id
    @param: video_name
    @return None
    """

    if len(url_list) == 0:
        raise Exception("can not get the url list")
    url = url_list[randrange(len(url_list))]
    if url is None:
        raise Exception("can not get download url")
    floder = os.path.join(os.getcwd(), 'video', user_id)
    if not os.path.exists(floder):
        os.mkdir(floder)
    video_path = os.path.join(floder, video_name + '.mp4')
    if not os.path.exists(video_path):
        url = custom_format_download_url(url)
        print('start to download the video, url: ' + url)
        res = session.get(url, headers=MOBIE_HEADERS)
        if res.status_code == 200:
            with open(video_path, "wb") as fp:
                for chunk in res.iter_content(chunk_size=1024):
                    fp.write(chunk)
            print('save video success, path: ' + video_path)
        else:  
            raise Exception("request to download video error")
    else:
        print("video already downloaded, skip!")
        pass

def custom_format_download_url(url):
    """自定义替换下载链接中的部分参数
    
    @param: url download_url
    """

    url = url.replace('watermark=1', 'watermark=0')
    ratio = re.compile('ratio=(\d+)p')
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
    print("data save success")

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

if __name__ == "__main__": 
    user_id = 110677980134

    uid, dytk = get_user_info(user_id)
    download_video(uid, dytk)