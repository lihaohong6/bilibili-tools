# Bilibili Tools

本项目用于分析B站[bilibili](https://www.bilibili.com)的弹幕、动态等内容。 

`Bilibili-Tools`包含的工具包括：
* 弹幕分析：查找有大量弹幕的视频时间段，方便在考古、补录播的时候快速跳转到有意思的片段。在高等进度条对时间过长的录播不起作用时很有用。
* 动态抓取：获取一个用户的所有动态并以容易阅读的方式打出，避免在查找动态时手动下滑页面。

## 安装

需要`python3.9`或更高。低版本`python`**有可能**可以正常运行本项目。

需要`bilibili_api`。若没有，请用`pip`安装。

使用时，将本项目下载下来，然后用`python`运行即可。

## 弹幕分析

分析一个视频中有大量弹幕的时间段。

用例：
```
python3 danmaku_analyzer.py BV1yF411Y7xs some_file.xml
```
分析`BV1yF411Y7xs`和存放在`some_file.xml`的弹幕（`xml`格式的弹幕可以用多种工具获取）. 
```
python3 danmaku_analyzer.py -f sources.txt -m 5
```
分析存储在`sources.txt`里面的BV号代表的视频。弹幕密度乘数被设为5。密度越高筛选时间段的条件就更苛刻。此处设为5比默认的低，因此会产生更多的时间段。

使用`python3 danmaku_analyzer.py -h`可以获取所有命令及其帮助。

## 动态抓取

用例
```
python3 dynamic_fetcher.py 16635128
```
可以获取`uid`为`16635128`的用户的所有动态并打印到控制台。程序对b站api返回的`json`数据进行了处理以提升可读性。

## 其他功能