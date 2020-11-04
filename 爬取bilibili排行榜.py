import requests
from bs4 import BeautifulSoup
import re
'''
本爬虫爬取B站排行榜的信息
'''


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 '
                  'Safari/537.36'}


# 获取页面，返回文本
def getHtml(url) -> str:
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        else:
            print(f'{url} 页面获取失败！！')
            exit(0)
    except Exception as e:
        print(e)
        print('出错的url是{}!!!'.format(url))


def readHtml():
    with open('1.html', 'r', encoding='utf-8') as f:
        return f.read()


def cawlBilibili_byUp(string):
    """
    :param string: 输入标签名
    """
    html = getHtml('https://www.bilibili.com/v/popular/rank/'+string)
    soup = BeautifulSoup(html, 'html.parser')
    found = soup.find('ul', class_='rank-list').find_all('li')
    account = 0
    for tip in found:
        account += 1
        text = tip.find('div', class_='info').find('a', class_='title')
        print(account, end=' ')
        video_name = re.search(r'>(.+)</a>', str(text)).group(1)
        video_url = 'https:' + text.get('href')
        up_name = (re.search(re.compile(r'</i>(.+)</span>', re.DOTALL),
                             str(tip.find('span', class_='data-box up-name'))).group(1)).strip()
        play_amount = re.search(re.compile(r'</i>(.+)</span>', re.DOTALL),
                                str(tip.find('span', class_='data-box'))).group(1).strip()
        print('Name:', video_name)
        print('url:', video_url)
        print('Up:', up_name)
        print('播放量：', play_amount)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def cawlBilibili_noUp(string):
    html = getHtml('https://www.bilibili.com/v/popular/rank/'+string)
    soup = BeautifulSoup(html, 'html.parser')
    found = soup.find('ul', class_='rank-list').find_all('li')
    account = 0
    for tip in found:
        account += 1
        text = tip.find('div', class_='info').find('a', class_='title')
        print(account, end=' ')
        video_name = re.search(r'>(.+)</a>', str(text)).group(1)
        video_url = 'https:' + text.get('href')
        play_amount = re.search(re.compile(r'</i>(.+)</span>', re.DOTALL),
                                str(tip.find('span', class_='data-box'))).group(1).strip()
        print('Name:', video_name)
        print('url:', video_url)
        print('播放量：', play_amount)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    # cawlBilibili_byUp('music')
    # cawlBilibili_byUp('origin')
    # cawlBilibili_noUp('movie')
    cawlBilibili_byUp('all')