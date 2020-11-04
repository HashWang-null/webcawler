import time
import requests
from bs4 import BeautifulSoup
import re
import json
import subprocess
import threading
import os
'''
本爬虫为多线程下载B站视频
作者：王瀚霆
使用方法：av_url修改为想要下载的B站视频网址 file_path修改为下载的文件路径/名称

         由于B站视频的视频文件和音频文件的地址是分开的， 所以本爬虫使用ffmpeg将音视频文件合并
         没有ffmpeg或者配置不正确的话自己想办法吧
         
         可以在download_video_from_Bilibili函数中修改线程数和音视频文件的名称/路径
         理论上线程数多少都行，但实测线程写多了或者网络不好的情况下（测试线程数96，但网络不好），会出现大量的
         timeout，程序虽然做了timeout的处理，会最多重新请求10次，但合成后的视频文件可能会损坏，原因未知。[timout多了会出现]（理论上不应该出错）
         （在网好的情况下试过1000线程，没出现timeout的情况，最后的文件也没问题，但请求速度没下载的速度快这样真的好嘛 淦）
         因此--线程数适当就好，本人不对乱写线程数导致最后的文件损坏负责。
         
         阿那个大会员的视频就少想了，别老想桃子吃 /@@/
         
这是本人的第四个爬虫，第一个爬视频的爬虫(第三个是单线程下B站）程序很多地方还不成熟，望大佬们多多见谅
欢迎交流学习！！ Q：2816293069
'''
head = {
    'Accept': '*/*',
    'accept-encoding': 'identity',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 '
                  'Safari/537.36'}


# 获取html
def getHtml(url) -> str:
    try:
        response = requests.get(url, headers=head, timeout=5)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        elif response.status_code == 206:
            response.encoding = 'utf-8'
            return response.content
        else:
            print(f'{url} 页面获取失败！！')
            print(response.status_code)
            exit(0)
    except Exception as e:
        print(e)
        print('出错的url是{}!!!'.format(url))
        exit(0)


# 解析html获得视频名称
def get_video_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.h1['title']


# 解析html获得视频的地址
def get_video_url(html):
    res = re.compile(r'__playinfo__=(.*?)</script><script>')
    text = re.search(res, html).group(1)
    js = json.loads(text)
    return js['data']['dash']['video'][0]['backupUrl'][0]


# 解析html获得音频的地址
def get_audio_url(html):
    res = re.compile(r'__playinfo__=(.*?)</script><script>')
    text = re.search(res, html).group(1)
    js = json.loads(text)
    return js['data']['dash']['audio'][0]['backupUrl'][0]


# 测试连接并获取资源大小信息
def text_connection(source_url):
    try:
        headers = head
        headers.update({'range': 'bytes=0-0'})
        res = requests.get(source_url, headers=headers, timeout=5)
        content_size = res.headers['Content-Range']
        video_size = int(re.match(r'bytes 0-0/(.+)', content_size).group(1))
        print('连接成功！')
        print('大小：', video_size, '字节    ', video_size / 1024 / 1024, 'MB')
        return video_size
    except Exception as e:
        print(e)
        print('连接失败')
        exit(0)


# 执行下载过程
def run(source_url, headers, filename):
    try_num = 0
    while try_num < 10:
        try:
            print('线程' + filename + '正在下载 ' + headers['range'])
            res = requests.get(source_url, headers=headers, timeout=20)
            with open(filename, 'wb') as f:
                f.write(res.content)
            print(filename + ' 下载完成.-------------------------->', res.headers['Content-range'])
            break
        except requests.exceptions.RequestException as e:
            try_num += 1
            print(filename, '------>timeout')
            continue
        except Exception as e:
            print(filename, e)
            exit(0)
    if try_num >= 10:
        print('下载失败')
        raise requests.exceptions.RequestException
        exit(0)


# 文件合并
def merge(n, filename):
    with open(filename, 'ab') as f:
        for i in range(n):
            f.write(open('{}'.format(i+1), 'rb').read())
    for i in range(n):
        os.remove('{}'.format(i+1))


# 多线程下载资源文件
def download(source_url, old_url, thread_num, final_name):
    """
    :param source_url: 资源Url地址
    :param old_url:  源网页的Url地址
    :param thread_num:  线程数量
    :param final_name:  合并后的文件名
    :return: None
    """
    threads = []
    head.update({'origin': 'https://www.bilibili.com'})
    head.update({"Referer": old_url})
    video_size = text_connection(source_url)
    positions = [0]
    for i in range(thread_num - 1):
        positions.append((i + 1) * (video_size // thread_num))
    positions.append(video_size)
    for i in range(1, len(positions)):
        try:
            headers = head.copy()
            headers.update({'range': 'bytes={}-{}'.format(positions[i - 1], positions[i] - 1)})
            filename = '{}'.format(i)
            t = threading.Thread(target=run, args=(source_url, headers, filename))
            t.start()
            threads.append(t)
            time.sleep(0.1)
        except Exception as e:
            exit(0)
    for thread in threads:
        thread.join()
    print("下载完成。")
    merge(thread_num, final_name)


# 使用 ffmpeg 将音视频合成
def video_add_mp3(mp4_name, mp3_file, outfile_name):
    cmd = 'ffmpeg -i ' + mp4_name + ' -i ' + mp3_file + ' -c:v copy -c:a aac -strict experimental ' + outfile_name
    try:
        subprocess.call(cmd)
    except Exception:
        print("FFmpeg配置不正确!")
        exit(0)
    # 删除音视频文件
    os.remove(mp4_name)
    os.remove(mp3_file)


def download_video_from_Bilibili(url, file_path):
    """

    :param url: 视频网址
    :param file_path: 保存的文件路径/名
    :return: None
    """
    html = getHtml(url)
    video_name = get_video_name(html)
    video_url = get_video_url(html)
    audio_url = get_audio_url(html)
    print('下载视频名称：', video_name)
    # 下载视频文件， 设置线程数和视频文件名称，第三个参数为线程数
    # download(video_url, url, 32, 'pre.mp4')
    # 下载音频文件， 设置线程数和音频文件名称，第三个参数为线程数
    download(audio_url, url, 32, 'pre.mp3')
    # video_add_mp3('pre.mp4', 'pre.mp3', file_path)
    print('程序执行完毕。')


if __name__ == '__main__':
    av_url = 'https://www.bilibili.com/video/BV1X4411H7ah?from=search&seid=8901137920625042167'
    filepath = 'D:/Desktap/python.mp4'
    download_video_from_Bilibili(av_url, filepath)