import requests
from bs4 import BeautifulSoup
import re
import json
import subprocess
import threading
import os

headers = {
    'Accept': '*/*',
    'accept-encoding': 'identity',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 '
                  'Safari/537.36'}


def getHtml(url) -> str:
    try:
        response = requests.get(url, headers=headers, timeout=5)
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


def get_video_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.h1['title']


# 下载
def download(download_url, filename, old_url):
    headers.update({'origin': 'https://www.bilibili.com'})
    headers.update({"Referer": old_url})
    headers.update({'range': 'bytes=0-0'})
    # 测试连接并获取资源大小
    try:
        response = requests.get(download_url, headers=headers, timeout=5)
        content_size = response.headers['Content-Range']
        video_size = int(re.match(r'bytes 0-0/(.+)', content_size).group(1))
        print('大小：', video_size, '字节    ', video_size / 1024 / 1024, 'MB')
    except Exception as e:
        print(e)
        return
    with open(filename, 'ab') as f:
        download_size = 0
        while download_size < video_size:
            print('{}已完成：'.format(filename), download_size / video_size * 100, '%')
            headers.update({'range': 'bytes={}-{}'.format(download_size, download_size + 99999)})
            download_size += 100000
            video_content = requests.get(download_url, headers=headers, timeout=5).content
            f.write(video_content)
        headers.update({'range': 'bytes={}-{}'.format(download_size, video_size - 1)})
        video_content = requests.get(download_url, headers=headers, timeout=5).content
        f.write(video_content)
    print('{}complete'.format(filename))
    pass


def video_add_mp3(mp4_name, mp3_file, outfile_name):
    cmd = 'ffmpeg -i ' + mp4_name + ' -i ' + mp3_file + ' -c:v copy -c:a aac -strict experimental ' + outfile_name
    subprocess.call(cmd, shell=True)
    os.remove(mp4_name)
    os.remove(mp3_file)


if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV1kz4y1o7kn'
    html = getHtml(url)
    video_name = get_video_name(html)
    video_url = get_video_url(html)
    print(video_url)
    audio_url = get_audio_url(html)
    download(video_url, 'pre.mp4', url)
    download(audio_url, 'pre.mp3', url)
    video_add_mp3('pre.mp4', 'pre.mp3', 'output.mp4')
    pass
