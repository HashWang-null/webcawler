import datetime
import requests
import xlrd
import xlwt
from lxml import etree
from bs4 import BeautifulSoup
import re
import json
import subprocess
import threading
import os


class Weather_clawer:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 '
                      'Safari/537.36'}


    def getHtml(self, url) -> str:
        try_time = 0
        while try_time < 10:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            except requests.ConnectTimeout:
                try_time += 1
                print('<timeout, try time:{}:>'.format(try_time))
                continue
            except Exception as e:
                print(e)
                exit(0)


    def get_month_weather(self, province, city):
        try:
            pre_html = self.getHtml('http://www.tianqihoubao.com/')
            pre_url = 'http://www.tianqihoubao.com/' + re.search(
                r'<td style="height: 22px"><a href="(.+)" title="' + province + '历史天气">' + province + '</a></td>',
                pre_html).group(1)
            pro_html = self.getHtml(pre_url)
            final_url = 'http://www.tianqihoubao.com/weather/' + re.search(
                r'<td style="height: 22px" align="center"><a href="(.+)" title="' + city + '历史天气查询">' + city + '</a></td>',
                pro_html).group(1)
            final_html = self.getHtml(final_url)
            xls = xlwt.Workbook(encoding='utf-8')
            worksheet = xls.add_sheet('{}天气'.format(city), cell_overwrite_ok=True)
            worksheet.write(0, 0, '城市')
            worksheet.write(0, 1, '日间天气情况')
            worksheet.write(0, 2, '日间风力方向')
            worksheet.write(0, 3, '日间最高温度')
            worksheet.write(0, 4, '夜间天气情况')
            worksheet.write(0, 5, '夜间风力方向')
            worksheet.write(0, 6, '夜间最低温度')
            soup = BeautifulSoup(final_html, 'html.parser')
            goal_list = soup.find('table').findAll('tr')
            for i in range(2, len(goal_list)):
                text = str(goal_list[i])
                res = re.findall(r'<td>(.+)</td>', text)
                for j in range(2, len(res)):
                    worksheet.write(i - 1, 0, city)
                    worksheet.write(i - 1, j - 1, res[j])
                    print(res[j])
                print("+++++++++++++++++++++")
            xls.save('{}最近一月天气.xls'.format(city))
        except AttributeError:
            print('没这省或城市，给爷重回初中学地理去.')
        except PermissionError:
            print('给老子看看你是不是把excel表格打开了')
        except Exception as e:
            print(type(e))
            print('发生了其他的一些错误')


    def get_year_weather(self, year):
        try:
            xls = xlwt.Workbook(encoding='utf-8')
            for i in range(1, 13):
                worksheet = xls.add_sheet('第{}月'.format(i), cell_overwrite_ok=True)
                month = '{}'.format(i).zfill(2)
                url = 'http://www.tianqihoubao.com/lishi/xian/month/{}{}.html'.format(year, month)
                html = self.getHtml(url)
                soup = BeautifulSoup(html, 'html.parser')
                trs = soup.find('table').findAll('tr')
                for m in range(1, len(trs)):
                    tds = trs[m].findAll('td')
                    date = tds[0].a.string.strip()
                    print(date)
                    worksheet.write(m-1, 0, date)
                    for n in range(1, len(tds)):
                        info = ''.join(re.findall(r'(\S+)+', str(tds[n].string)))
                        worksheet.write(m-1, n, info)
                        print(info)
                    print('-----------------------------------------------------------')
            xls.save('整年西安天气.xls')
        except PermissionError:
            print('给老子看看你是不是把excel表格打开了')
        except Exception as e:
            print(type(e))
            print('发生了其他的错误')


if __name__ == '__main__':
    start = datetime.datetime.now()
    Weather_clawer().get_year_weather(2019)
    end = datetime.datetime.now()
    print('Running time: %s Seconds' % (end - start))

