# -*- coding: utf-8 -*-


import scrapy
from leyuedu.items import LeyueduItem
import time
from urllib.parse import urljoin
from scrapy import Request

class LreadSpider(scrapy.Spider):
    name = 'lread'
    allowed_domains = ['www.lread.net']
    start_urls = 'https://www.lread.net/quan/'

    def start_requests(self):
        yield Request(url=self.start_urls, callback=self.parse_index)

    def parse_index(self, response):
        novellist = response.css('div#main div.novellist')
        for each in novellist:
            novel_type = each.xpath('./h2/text()').extract_first()
            ul = each.xpath('./ul//li')
            for li in ul:
                url = li.xpath('./a/@href').extract_first()
                url = url[:4] + 's' + url[4:]
                title = li.xpath('./a/text()').extract_first()
                auth = li.xpath('./text()').extract_first().strip('/作者:')
                info_list = {'novel_type':novel_type, 'title':title, 'auth':auth}
                time.sleep(0.1)
                yield Request(url=url, callback=self.parse_detail,meta=info_list)

    def parse_detail(self, response):
        dd = response.css('div.box_con div#list dl dd')
        for a in dd:
            href = a.css('a::attr(href)').extract_first()
            href = urljoin(self.start_urls, href)
            art_title = a.css('a::text').extract_first()
            art_num_temp = href.split('/')[-1].strip('.html')
            if art_num_temp:
                art_num = int(art_num_temp)
            else:
                art_num = 0
            info_list = {'title':response.meta['title'], 'auth':response.meta['auth'], 'art_title':art_title,
                         'novel_type':response.meta['novel_type'], 'art_num':art_num}
            time.sleep(0.1)
            yield Request(url=href, callback=self.get_text, meta=info_list)

    def get_text(self, response):
        item = LeyueduItem()
        text = response.css('div.content_read div.box_con div.content::text').extract()
        text = ''.join(text)
        item['title'] = response.meta['title']
        item['auth'] = response.meta['auth']
        item['art_title'] = response.meta['art_title']
        item['art_num'] = response.meta['art_num']
        item['text'] = text
        item['novel_type'] = response.meta['novel_type']
        # self.logger.info((response.meta['title'],response.meta['auth'],response.meta['art_title'], text))
        # return item
        yield item