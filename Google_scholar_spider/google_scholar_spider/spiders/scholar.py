# -*- coding: utf-8 -*-
import scrapy

class ScholarSpider(scrapy.Spider):
    name = 'scholar'
    # allowed_domains = ['scholar.google.com']

    # 关键词通过format里面的第二个参数替换，爬取数量由i的范围控制
    start_urls = ['https://scholar.google.com/scholar?start={}&q={}'.format(str(i), 'psychology') for i in range(0,101,10)]

    def parse(self, response):
        for article in response.xpath('//*[@id="gs_ccl_results"]/div'):
            yield {
                'title':' '.join(article.xpath('.//h3/a//text()').extract()),
                'authors':' '.join(article.xpath('.//div[@class="gs_a"]//text()').extract()),
                'abstract':' '.join(article.xpath('.//div[@class="gs_rs"]//text()').extract()),
                'url': article.xpath('.//h3/a/@href').extract_first(),
            }