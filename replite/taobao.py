import requests
import re

'''
User Agent：用户代理，简称 UA，它是一个特殊字符串头，使得服务器能够识别客户使用的操作系统及版本、CPU 类型、浏览器及版本、
浏览器渲染引擎、浏览器语言、浏览器插件等。
标准格式： 浏览器标识 (操作系统标识; 加密等级标识; 浏览器语言) 渲染引擎标识 版本信息
'''


def getHTMLText(url):
    try:
        headers = {
            # "user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            "cookie": "_uab_collina=157258226625083933457665; thw=cn; t=36d1cd24cf0143fb6accdf025534d197; enc=97GhrHhKkErSIlgzQuOf4gDv8yB1IDMrzS%2FqNp8OhQXosfA5%2Bpm6Vj4%2B%2FjCYIIsIglI%2FeakHaMTRg2bsOCGe%2Fg%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; cookie2=130c64bc2ccdc80f7d3858f7c4143707; _tb_token_=ede063be6e3ee; XSRF-TOKEN=a5e7e17c-f1d8-4ece-8f63-20dd0adc170c; mt=ci=0_0; cna=PpdBFupPaykCAbdAPqcqw59D; isg=BFlZdWsdY9ah6DznWNPShWvxaEwz5k2YGu7yC3sO5wD_gngUwTA4a72QgAZROuXQ; l=cBLufjhqqvUwqS6yBOCZhurza7799IRAguPzaNbMi_5CU6L65G7Oovk9xFp6cjWdOrYp4-ERe5p9-eteiNF7dhspXUJ1."
        }
        # 不模拟浏览器登录，会跳转到淘宝登录页
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "爬取失败"


def parsePage(ilt, html):
    try:
        plt = re.findall(r'\"view_price\"\:\"[\d\.]*\"', html)
        tlt = re.findall(r'\"raw_title\"\:\".*?\"', html)
        for i in range(len(plt)):
            price = eval(plt[i].split(':')[1])
            title = eval(tlt[i].split(':')[1])
            ilt.append([price, title])
    except:
        print("解析信息失败")


def printGoodsList(ilt):
    tplt = "{:4}\t{:8}\t{:16}"
    print(tplt.format("序号", "价格", "商品名称"))
    count = 0
    for g in ilt:
        count = count + 1
        print(tplt.format(count, g[0], g[1]))


def main():
    goods = '书包'
    depth = 3
    start_url = 'https://s.taobao.com/search?q=' + goods
    infoList = []
    for i in range(depth):
        try:
            url = start_url + '&s=' + str(48 * i)
            html = getHTMLText(url)
            parsePage(infoList, html)
        except:
            continue
    printGoodsList(infoList)


main()
