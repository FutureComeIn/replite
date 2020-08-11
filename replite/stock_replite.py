import requests
from bs4 import BeautifulSoup
import traceback
import re


def getChinese():
    a_str = '404 not found 张三 23 深圳'

    # 方法一：正则表达式 [^\x00-\xff], 只匹配非ASCII码字符(也称双字节字符), 利用汉字为: 双字节字符的原理
    a_list = re.findall(r'[^\x00-\xff]', a_str)

    # 方法二：正则表达式 [\u4e00-\u9fa5], 只匹配汉字，依据汉字的Unicode码表: 从u4e00~u9fa5, 即代表了符合汉字GB18030规范的字符集
    a_list2 = re.findall(r'[\u4e00-\u9fa5]', a_str)

    # 方法三：使用正则表达式: \w+, re.A 即指ASCII编码, 可匹配除中文以外的单词字符, 得到新列表
    # 利用 去同存异 的方法 (不适合单独 带中文和非中文 的字符串)
    a_list3 = a_str.split(" ")  # ['404', 'not', 'found', '张三', '23', '深圳']
    res = re.findall(r'\w+', a_str, re.A)  # ['404', 'not', 'found', '23']
    new_list = []
    for i in a_list3:
        if i not in res:
            new_list.append(i)
    print("".join(new_list))

    print(a_list)
    print(a_list2)
    # 输出结果


def getHTMLText(url, code='utf-8'):
    try:
        r = requests.get(url)
        r.raise_for_status()
        print(r.apparent_encoding)  # 先查看一下网页内容所用的编码
        r.encoding = code  # 性能优化：对于定向爬虫，爬取的网站固定，直接给定编码，节省r.apparent_encoding分析内容是什么编码的时间
        return r.text
    except:
        # traceback.print_exc()
        return "爬取失败"


def getStockList(lst, stockURL):
    html = getHTMLText(stockURL)  # 性能优化：东方财富网是 GB1212 编码
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        try:
            href = i.attrs['href']
            lst.append(re.findall(r"[s][hz]\d{6}", href)[0])
        except:
            continue


def getStockInfo(lst, stockURL, fpath):
    count = 0
    for stock in lst:
        # http://finance.sina.com.cn/realstock/company/sz300059/nc.shtml
        url = stockURL + stock + "/nc.shtml"
        html = getHTMLText(url, 'GB2312')
        try:
            if html == "":
                continue
            infoDict = {}
            infoDict.update({'股票名称：': '东方财富'})
            soup = BeautifulSoup(html, 'html.parser').find_all('tbody')[3]
            ths = soup.find_all('th')
            tds = soup.find_all('td')
            for i in range(len(ths)):
                key_list = re.findall(r'[\u4e00-\u9fa5]', ths[i].text)
                key = ''.join(key_list)
                value = tds[i].text
                infoDict[key] = value
            with open(fpath, 'a', encoding='utf-8') as f:
                f.write(str(infoDict) + '\n')
                count = count + 1  # 获取一个股票信息就写入文件，所以可以count=count+1
                print("\r当前读取个股的数量进度: {:.2f}%".format(count * 100 / len(lst)), end="")
                # \r 代表回车，也就是打印头归位，(光标)回到当前行的开头。
                # end=''作为print()BIF的一个参数，会使该函数关闭“在输出中自动包含换行”的默认行为。其原理是：为end传递一个空字符串，
                # 这样print函数不会在字符串末尾添加一个换行符，而是添加一个空字符串。这个只有Python3有用，Python2不支持
        except:
            count = count + 1
            print("\r当前读取个股的数量进度: {:.2f}%".format(count * 100 / len(lst)), end="")
            traceback.print_exc()
            continue


def main():
    stock_list_url = 'http://quote.eastmoney.com/stocklist.html'
    stock_info_url = 'http://finance.sina.com.cn/realstock/company/'  # 新浪股票网址形式： sz300059/nc.shtml
    output_file = '/Users/v_yuanxiwen/Desktop/BaiduStockInfo.txt'
    slist = []
    # 访问 stock_list_url东方财富网 跳转到 http://quote.eastmoney.com/center/gridlist.html#hs_a_board, 原码界面已经获取不到其他个股的股票代码
    # 只获取到了 它自己的 东方财富股票代码 sist=['sz300059']
    getStockList(slist, stock_list_url)
    # 根据股票列表 到 对应股票页面 获取股票信息 并存储到文件
    getStockInfo(slist, stock_info_url, output_file)


main()
