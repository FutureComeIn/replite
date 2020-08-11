from selenium import webdriver
from selenium.webdriver.chrome.options import Options

req_url = "https://www.baidu.com"
chrome_options = Options()
# 设置chrome浏览器无界面模式
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)
# 开始请求
browser.get(req_url)
# 打印页面源代码
print(browser.page_source)
# 关闭浏览器
browser.close()

