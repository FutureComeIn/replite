# coding=utf-8

import requests

# 爬取 亚马逊图书

url = "https://www.amazon.cn/gp/product/B01M8L5Z3Y"
try:
    kv = {'user-agent': 'Mozilla/5.0'}   #告诉亚马逊，以火狐浏览器的形式访问你，而不是requests库
    r = requests.get(url, headers=kv)
    r.raise_for_status()   # 当 返回状态 不是200，执行except
    r.encoding = r.apparent_encoding
    print(r.text[:1000])  # 截取前1000个字符 [1000:2000] ; 最后500个字符 [-500:]
except:
    print("爬取失败")


# 用 百度搜索接口 获得 搜索内容  (360搜索接口：http://www.so.com/s?q=xxx）
'''
keyword = "Python"
try:
    kv = {'wd': keyword}
    r = requests.get("http://www.baidu.com/s", params=kv)
    print(r.request.url)
    r.raise_for_status()
    print(len(r.text))
except:
    print("爬取失败")
'''

# 爬取图片
'''
import os
url="https://dss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=1039784932,1678053317&fm=26&gp=0.jpg"
root="/Users/v_yuanxiwen/Desktop/"  # 自己取名，root="/Users/v_yuanxiwen/Desktop/girls.jpg"
path=root+url.split('/')[-1]
try:
    if not os.path.exists(root):
        os.mkdir(root)
    if not os.path.exists(path):
        r=requests.get(url)
        with open(path,'wb') as f:
            f.write(r.content)
            f.close()
            print("文件保存成功")
    else:
        print("文件已存在")
except:
    print("爬取失败")
'''

# ip 地址查询
# url = "http://m.ip138.com/ip.asp?ip="
# try:
#     r = requests.get(url + '192.168.43.1')
#     r.raise_for_status()
#     r.encoding = r.apparent_encoding
#     print(r.text[-500:])
# except:
#     print("爬取失败")


