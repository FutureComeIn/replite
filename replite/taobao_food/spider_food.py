import time

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq

# (因为 PhantomJS 已停止更新，且据说selenium 不再支持 PhantomJS,
# 另外 chrome、firefox 已经开始支持 无头模式(headless)，所以PhantomJS不再有优势)
# 设置chrome浏览器无界面模式
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=chrome_options)

# browser2 = webdriver.phantomjs  #还支持 PhantomJS
# browser3 = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def search():
    try:
        print("正在搜索")
        browser.get('https://www.jd.com')
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#key'))
        )
        search_submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > div > div.form > button > i')))
        search_input.send_keys('美食')
        search_submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')))
        get_pro()
        return total.text
    except TimeoutException:
        return search()


def next_page(page_number):
    try:
        print("下一页:" + str(page_number))
        to_page_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input'))
        )
        turn_submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a'))
        )
        to_page_input.clear()
        to_page_input.send_keys(page_number)
        turn_submit.click()
        # 滑动到底部，加载出后三十个货物信息
        # 等待高亮页码、滑动到底部 的操作先后执行的分析：如果等待高亮页码出来了，说明已经在底部了，再滑动到底部还是只有30个商品
        # 目前首页，还是只有30个商品，在模拟浏览器向下拖动网页时,出现 StaleElementReferenceException 异常(由于数据更新不及时)
        # 一般两种处理：滑动到底部后使用time.sleep() 给浏览器充足的加载时间；捕获该异常进行相应的处理。 然并软
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 高亮的页数 等于 跳转的页数 ，即请求成功 (加一个等待时间，不等待可能高亮的页数不能加载到)
        time.sleep(1)
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.curr'), str(page_number))
        )
        get_pro()
    except TimeoutException:
        print('重新请求')
        next_page(page_number)


def get_pro():
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList .gl-item .gl-i-wrap')))
        # page_source 获取页面源代码
        html = browser.page_source
        doc = pq(html)
        items = doc('#J_goodsList .gl-item .gl-i-wrap').items()
        # print(len(list(items)))
        for item in items:
            product = {
                'image': item.find('.p-img').find('img').attr('src'),
                'price': item.find('.p-price').text(),
                'title': item.find('.p-name').text(),
                'deal': item.find('.p-commit').text()[:-3],
                'shop': item.find('.p-shop').text(),
            }
            print(product)
            # 存储到mongo，每页会少30条数据
            # save_to_pymongo(product)
    except StaleElementReferenceException:
        print('turn_page: StaleElementReferenceException')
        browser.refresh()


MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'food'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def save_to_pymongo(result):
    try:
        if db[MONGO_TABLE].insert_one(result):
            print("存储到mongodb成功：", result)
    except:
        print("存储到mongodb失败", result)


def main():
    try:
        total = search()
        print('页数：' + total)
        for i in range(2, int(2) + 1):
            next_page(i)
    except:
        print("出错啦")
    finally:
        browser.close()


if __name__ == '__main__':
    main()
