# -*- coding: utf-8 -*-
import scrapy



class ScienceSpider(scrapy.Spider):
    name = 'science'
    # allowed_domains = ['http://science.sciencemag.org/content/356/6342']
    # start_urls = ['http://science.sciencemag.org/content/by/year/2017']
    # 卷数范围需要手动设置
    start_urls = ['http://science.sciencemag.org/content/355/{}'.format(str(6320 + i)) for i in range(23)]

    def parse(self, response):
        '''
        # Gt All year Jurnals link
        all_year_urls = response.xpath(
            '//a[@lass="highlight-image-linked"]/@href'
        ).extract()
        for week_url in all_year_urls:
            yield scrapy.Request(response.urljoin(week_url))
        '''
        # Get article URLs and yield Requests
        article_urls = response.xpath('//a[@class="highwire-cite-linked-title"]/@href').extract()
        for url in article_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_article)


    def parse_article(self, response):
        yield {
            'title': response.xpath('//h1[@class="article__headline"]/div/text()').extract_first(),
            'author':[li.xpath('./span/text()').extract() for li in response.xpath('//*[@id="contrib-1"]|//*[@id="contrib-1"]/following-sibling::*')],
            'affiliations': response.xpath('//ol[@class="affiliation-list"]/li/address//text()').extract(),
            'abstract': response.xpath('//*[@id="p-2"]/text()').extract(),
            'url': response.url
            #'keyword': response.xpath('//*[@id="main-content"]/article//div[@class="KeywordGroup"]/span/text()').extract_first(),
        }
