# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from springer_spider.items import SpringerSpiderItem

class JournalsSpider(scrapy.Spider):
    name = 'springer'
    # allowed_domains = ['https://link.springer.com/journal/11257']
    # start_urls = ['https://link.springer.com/journal/11257/']
    # 需要手动添加某杂志的所有文章的搜索页面
    start_urls = ['https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=11257']
    '''
    def parse(self, response):
        for article in response.xpath('//*[@id="results-list"]/li'):
            yield{
                'title':article.xpath('./h2/a/text()').extract_first(),
                'abstract':article.xpath('./p[@class="snippet"]/text()').extract_first(),
            }

        for a in response.xpath('//*[@id="kb-nav--main"]//div[@class="functions-bar functions-bar-bottom"]/form/a'):
            yield response.follow(a, callback=self.parse)
    
    
    def parse_article(self, response):
        l = ItemLoader(item=SpringerSpiderItem(), response=response)
        l.add_xpath('title', '//*[@id="main-content"]/article//div[@class="MainTitleSection"]/h1/text()')
        l.add_xpath('author', '//*[@id="authorsandaffiliations"]/div/ul/li/span/text()')
        l.add_xpath('affiliations', '//*[@id="authorsandaffiliations"]/div/ol/li/span[@class="affiliation__item"]//text()')
        l.add_xpath('abstract', '//*[@id="Abs1"]/p/text()')
        l.add_xpath('keyword', '//*[@id="main-content"]/article//div[@class="KeywordGroup"]/span/text()')

        return l.load_item()
    '''


    def parse(self, response):
        # Get next index URLs and yield Requests
        next_urls = response.xpath(
            '//*[@id="kb-nav--main"]//div[@class="functions-bar functions-bar-bottom"]/form/a/@href'
        ).extract()
        for next_url in next_urls:
            yield scrapy.Request(response.urljoin(next_url))

        # Get article URLs and yield Requests
        article_urls = response.xpath('//*[@id="results-list"]/li/h2/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article)

    def parse_article(self, response):
        yield {
            'title': response.xpath('//*[@id="main-content"]/article//div[@class="MainTitleSection"]/h1/text()').extract_first(),
            'author': [a.replace('\u00A0', '') for a in response.xpath('//*[@id="authorsandaffiliations"]/div/ul/li/span/text()').extract()],
            'affiliations': response.xpath('//*[@id="authorsandaffiliations"]/div/ol/li/span[@class="affiliation__item"]//text()').extract(),
            'abstract': response.xpath('//*[@id="Abs1"]/p/text()').extract(),
            'url': response.url

        }
