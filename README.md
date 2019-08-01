# 抖音寻找漂亮小姐姐or帅气小哥哥，并下载她（他）们的所有作品

![](./tmp/douyin.gif)
![](./tmp/douyin-console.gif)

原本只是写了一个下载抖音无水印视频的小脚本，后面突然想到了[Douyin-Bot](https://github.com/wangshub/Douyin-Bot/blob/master/README.md)这个项目，觉得是可以结合操作的，达到完全自动化，所以就引入了相关的代码，并进行了一定的逻辑修改，实现了目前的流程。

> Python + ADB实现抖音的控制浏览 -> 复制视频链接 -> 提取用户信息 -> 程序下载用户所有视频


### ⏰ 如果你只需要下载功能，可以直接查看 [DOWNLOAD.md](https://github.com/renyijiu/douyin_downloader/blob/master/DOWNLOAD.md)，无需查看后续内容


## 环境安装

请在使用项目之前确保你的手机可以正常使用adb控制，相关信息可以网上搜索。**另外复制内容需要使用clipper.apk，在apks中有提供，[项目地址](https://github.com/majido/clipper)，可自行查看，另外 *请允许此app后台运行，自测发现未后台运行会导致获取不到剪贴板内容***

```
$ git clone git@github.com:renyijiu/douyin_downloader.git
$ cd douyin_downloader
$ virtualenv -p python3.6 douyin
$ source douyin/bin/activate
$ pip install -r requirements.txt
```

## 使用

1. 打开抖音app
2. 执行 python douyin-bot.py

## ⚠注意️
1. 具体Python + ADB实现抖音的控制浏览，可以查看[Douyin-Bot](https://github.com/wangshub/Douyin-Bot/blob/master/README.md)去了解，这里不做介绍了
2. 目前ADB获取剪贴板操作，通过 [clipper.apk](https://github.com/majido/clipper)实现，如果你有更好的方案，欢迎提出更改，感谢🙏！
3. 目前提供的配置是基于自己的 *魅族pro5* 测试机，不同机型请自行修改（欢迎提供你的配置）
- `config.json`配置文件参考：
    - `center_point`: 屏幕中心点`(x, y)`，区域范围`(rx, ry)`，主要翻页使用
    - `left_swipe_point`: 起始点坐标`(x, y)`，区域范围`(rx, ry)`，分享按钮时活动获取复制链接使用
    - `follow_bottom`: 关注按钮坐标`(x, y)`, 区域范围`(rx, ry)`
    - `star_bottom`: 点赞按钮坐标`(x, y)`，区域范围`(rx, ry)`
    - `share_bootom`: 分享按钮坐标`(x, y)`，区域范围`(rx, ry)`
    - `copy_link_bottom`: 复制链接按钮（分享按钮点击后弹出）`(x, y)`，区域范围`(rx, ry)`
    - `crop_img`: 截图范围起始点坐标`(x, y)`，区域范围`(width, height)`, 从页面截图裁剪部分（为了去除头像之类的干扰信息），另外范围过大可能导致图像过大使接口报错，请自行增加压缩操作

## 感谢
站在巨人的肩膀
1. [Douyin-Bot](https://github.com/wangshub/Douyin-Bot)
2. [clipper](https://github.com/majido/clipper)

## 建议反馈
请直接在[Github](https://github.com/renyijiu/douyin_downloader/issues)上开新的issue，描述清楚你的问题需求即可。
