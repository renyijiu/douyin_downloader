### douyin_downloader

> Only Python 3.6 is supported.

好久不写Python了，尝试使用了下[requests-html](https://github.com/oldani/requests-html)，下载指定用户的所有抖音视频

#### 注意
以前一直使用`requests`库，这次尝试使用了下`requests-html`，而`requests-html`官方介绍只支持`python3.6`

#### 环境安装

```shell
$ git clone git@github.com:renyijiu/douyin_downloader.git
$ cd douyin_downloader
$ virtualenv -p python3.6 douyin
$ source douyin/bin/activate
$ pip install -r requirements.txt

```

**因为`requests-html`为了完整支持JavaScript，所以依赖库中会从google下载chromium，请确保你的网络可以正常访问google相关网站，以确保能够顺利下载**

#### 使用

1. 将你所需要下载的分享链接写到`share-url.txt`文件中，一行一个链接，然后执行`python douyin.py`即可
2. 使用命令行方式，`python douyin.py --urls=url1,url2,url3`，多个地址使用`,`分割

#### 结果

1. data目录下保存了请求到的json数据，减少重复请求，另外后续你也可以提取自己所需的信息，例如视频介绍等
2. video目录下保存了用户的抖音视频，按照用户id建立对应的文件夹

#### 建议反馈

直接在[Github](https://github.com/renyijiu/douyin_downloader/issues)上开新的issue
