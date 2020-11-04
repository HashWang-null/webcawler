import requests
from bs4 import BeautifulSoup
import re

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
            print("status code: {}".format(response.status_code))
            exit(0)
    except Exception as e:
        print(e)
        print("url 出错 url:{}".format(url))
        exit(0)


# 爬取豆瓣top电影的信息
def cawl_douban():
    for i in range(10):
        count = 0
        html = getHtml('https://movie.douban.com/top250?start={}&filter='.format(i * 25))
        soup = BeautifulSoup(html, 'html.parser')
        found = soup.find('ol').find_all('li')
        for tip in found:
            count += 1
            pattern = re.compile(r'<p class="">(.+)</p>', flags=re.DOTALL)
            print(i * 25 + count, tip.img['alt'], tip.img['src'])
            # 下载影片的封面
            # downloadPicture(tip.img['src'], i*25+count)
            print(tip.a['href'])
            print((re.findall(pattern, str(tip.p))[0]).replace('<br/>', ''))


def downloadPicture(url, count):
    try:
        cont = requests.get(url, headers=headers, timeout=5)
        with open('picture/{}.jpg'.format(count), 'wb') as f:
            f.write(cont.content)
    except Exception as e:
        print(e)
        return


# 根据图片地址下载图片，name为文件名
def saveImg(url, name):
    with open(name + '.jpg', 'wb') as f:
        f.write(requests.get(url, headers=headers, timeout=5).content)


if __name__ == '__main__':
    cawl_douban()
