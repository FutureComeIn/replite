import json
import os
import re
import time
from hashlib import md5
from json import JSONDecodeError
from urllib.parse import urlencode

import pymongo
import requests
from bs4 import BeautifulSoup

'''
网页分析：Ajax加载的数据 在XHR 可以找到，然后点击Preview可以发现第一个数据的data有我们想要的数据
在 街拍首页 下拉刷新查看加载的offset，每次加载20条数据，data是json数据，里面的article_url,是图集详情页的url
'''

# 有隐形的图片验证，偶尔出现，cookie是重要参数 这是解决data：none的关键
headers = {
    'cookie': 'tt_webid=6788065855508612621; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6788065855508612621; csrftoken=495ae3a5659fcdbdb78e255464317789; s_v_web_id=k66hcay0_qsRG7emW_x2Qj_4R3o_AeAG_iT4JWmz83jzr; tasessionId=23dn3qk0f1580738708512',
    'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

MONGO_URL = 'localhost'
MONGO_DB = 'toutiao'
MONGO_TABLE = 'toutiao'
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def save_to_mongo(result):
    if db[MONGO_TABLE].insert_one(result):
        print('Successfully Saved to Mongo', result)
        return True
    return False


def get_page_index(offset, keyword):
    data = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': int(time.time()),  # 获取时间戳
        # _signature 今日头条的加密参数
        # '_signature': 'z4xcrAAgEBD2co4X.MwGv8-NHbAAJEqabZGG0Z0u12eqluwW2tmq6RPGzdk5kOC3u9whTQSaqLpBN.fHcACm.Cb2VC8LlLNTAY2XUsWh9yQmAbHyAlSTqIYT6tYwgrKJBGy'
    }
    index_url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    try:
        response = requests.get(index_url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('请求首页失败')
        return None


def parse_page_index(text):
    try:
        data = json.loads(text)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(article_url):
    try:
        # 不加headers, 内容只有 <html><head></head><body></body></html>
        response = requests.get(article_url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('请求图集详情页失败')
        return None


def parse_page_detail(article_url_text, article_url):
    soup = BeautifulSoup(article_url_text, 'lxml')
    result = soup.select('title')
    title = result[0].get_text() if result else ''
    images_pattern = re.compile('gallery: JSON.parse\("(.*)"\)', re.S)
    result = re.search(images_pattern, article_url_text)
    if result:
        # 将json字符串转成Python对象
        # 正则表达式中，group（）用来提出分组截获的字符串，（）用来分组,0返回整体
        data = json.loads(result.group(1).replace('\\', ''))
        print(data)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            images2 = []
            for image in images:
                # 在result.group(1)处 直接将 \\\u002F 替换成 / 又有其他问题，所以拿到图片的url后再替换
                download_image(image.replace('u002F', '/'), title)
                images2.append(image.replace('u002F', '/'))
            return {
                'title': title,
                'url': article_url,
                'images': images2
            }


def download_image(url, title):
    print('Downloading', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, title)
        return None
    except ConnectionError:
        return None


def save_image(content, title):
    c_title = title.replace('：', '_').replace('，', '_').replace(':', '_').replace('。', '')
    if not os.path.exists(c_title):
        os.mkdir(c_title)
    file_path = '{0}/{1}.{2}'.format(os.getcwd() + '/' + c_title, md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()
    else:
        print("已下载", file_path)


# 单个图集url详情测试
def single():
    text = requests.get('http://www.toutiao.com/group/6821658978578072067/', headers=headers).text
    result = parse_page_detail(text, 'http://www.toutiao.com/group/6821658978578072067/')
    print(result)


if __name__ == '__main__':
    index_url_text = get_page_index(20, '街拍')
    article_urls = parse_page_index(index_url_text)
    for article_url in article_urls:
        if not article_url is None:
            if 'group' in article_url:
                article_url_text = get_page_detail(article_url)
                result = parse_page_detail(article_url_text, article_url)
                if result:
                    save_to_mongo(result)
