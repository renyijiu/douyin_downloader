# douyin_downloader

![](./tmp/flower.jpg)


下载指定用户的所有抖音视频以及用户收藏的视频（无水印）

## 注意⚠️

> Only Python 3.6 is supported.

使用了[requests-html](https://github.com/oldani/requests-html)，而`requests-html`官方介绍只支持`python3.6`

## 环境安装

```shell
$ git clone git@github.com:renyijiu/douyin_downloader.git
$ cd douyin_downloader
$ virtualenv -p python3.6 douyin
$ source douyin/bin/activate
$ pip install -r requirements.txt

```

⚠️ **`requests-html`为了完整支持JavaScript，所以依赖库会从google下载chromium，请确保你的网络可以正常访问google相关网站，让依赖能够顺利下载**

## 使用

可以执行 `python douyin.py -h` 查看详细说明

### 文件方式

1. 将你所需要的下载链接写到目录下`share-url`文件中，一行一个链接
2. 执行`python douyin.py`下载用户的所有抖音视频
3. 执行`python douyin.py -l` 或者 `python douyin.py --like` 下载用户所有收藏的视频

### 命令行模式

1. `python douyin.py --urls=url1,url2,url3`，多个地址使用`,`分割，下载用户所有的视频
2. `python douyin.py --urls=url1,url2,url3 --like`,下载用户收藏的所有视频
3. `python douyin.py -s -u single_video_url`，下载单个分享视频

## 结果

1. data目录下保存了请求到的json数据，减少重复请求，另外后续你也可以提取自己所需的信息，例如视频介绍等；格式 video_id - [favorite] - cursor.json
2. video目录下保存了用户的抖音视频，按照用户id建立对应的文件夹; favorite目录下存放了用户收藏的视频，也是按照用户id建立对应的文件夹

## 建议反馈

请直接在[Github](https://github.com/renyijiu/douyin_downloader/issues)上开新的issue，描述清楚你的问题需求即可。
