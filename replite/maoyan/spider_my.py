import json
import re
from multiprocessing import Pool

import requests


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            # 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        print(r.url)
        return r.text
    except:
        return "请求url失败"


def parse_one_page(text):
    pattern = re.compile('<dd>.*?board-index-.*?>'
                         '(\d+)'
                         '</i>.*?data-src="'
                         '(.*?)'
                         '".*?data-val.*?>'
                         '(.*?)'
                         '</a>.*?star">'
                         '(.*?)'
                         '</p>.*?releasetime">'
                         '(.*?)'
                         '</p>.*?integer">'
                         '(.*?)'
                         '</i>.*?">'
                         '(.*?)'
                         '</i></p>.*?</dd>', re.S)  # re.S 表示 .*? 也匹配文本中的 换行
    dds = re.findall(pattern, text)
    for item in dds:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }


def write_to_file(content):
    # json.dumps()用于将字典形式的数据转化为字符串(即，写入到文件中的数据将是 双引号)
    # json.loads()用于将字符串形式的数据转化为字典
    # json.dumps 序列化时对中文默认使用的ascii编码,想输出真正的中文需要指定ensure_ascii=False
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(offset):
    url = "https://maoyan.com/board/4?offset=" + str(offset)
    text = get_one_page(url)
    for item in parse_one_page(text):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    # 多进程实现 秒抓: 提供指定数量的进程池，给用户调用，哪个进程没有满，就会创建新的进程处理这个请求
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
