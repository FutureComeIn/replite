# -*- coding: utf-8 -*-
import scrapy
import re


class StocksSpider(scrapy.Spider):
    name = 'stocks'
    # allowed_domains = ['baidu.com']
    start_urls = ['http://quote.eastmoney.com/stocklist.html']

    def parse(self, response):
        for href in response.css('a::attr(href)').extract():
            try:
                stock = re.findall(r"[s][hz]\d{6}",href)[0]
                url = 'http://finance.sina.com.cn/realstock/company/'+ stock+'/nc.shtml'
                yield scrapy.Request(url,callback=self.parse_stock)
            except:
                continue
    def parse_stock(self,response):
        infoDict = {}
        stockInfo = response.css('tbody')[3]
        ths = stockInfo.css('th::text').extract()
        ths.remove('：')
        tds = stockInfo.css('td::text').extract()
        for i in range(len(ths)):
            key_list = re.findall(r'[\u4e00-\u9fa5]', ths[i])
            key = ''.join(key_list)
            value  = tds[i]
            infoDict[key] = value
        infoDict.update({'股票名称':'东方财富'})
        yield infoDict
