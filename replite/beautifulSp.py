# encoding=utf-8

import requests
from bs4 import BeautifulSoup  # 可以理解为：从bs4（BeautifulSoup4）库导入BeautifulSoup类
                               # 这个直接将BeautifulSoup 类导入到当前命名空间，直接使用，不需要再带包名。
import bs4

'''
r = requests.get("http://python123.io/ws/demo.html")
demo = r.text
print(demo)
soup = BeautifulSoup(demo, 'html.parser')
print(soup.prettify())
'''

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

def fillUniversityList(ulist, html):
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find('tbody').children:
        if isinstance(tr, bs4.element.Tag):
            tds = tr('td')
            ulist.append([tds[0].string, tds[1].string, tds[2].string])

def printUniversity(ulist, num):
    # print("{:^10}\t{:^6}\t{:^10}".format("排名", "学校名称", "总分"))
    # for i in range(num):
    #     u = ulist[i]
    #     print("{:^10}\t{:^6}\t{:^10}".format(u[0], u[1], u[2]))
    tplt = "{0:^10}\t{1:{3}^10}\t{2:^10}"
    print(tplt.format("排名", "学校名称", "总分", chr(12288)))
    for i in range(num):
        u = ulist[i]
        print(tplt.format(u[0], u[1], u[2], chr(12288)))

def main():
    ulist = []
    url = 'http://www.zuihaodaxue.cn/zuihaodaxuepaiming2016.html'
    fillUniversityList(ulist, getHTMLText(url))
    printUniversity(ulist, 20)

main()
