# 学术摘要爬虫
### Springer_spider
可以实现对某期刊所有文章摘要的爬取，基于Scrapy框架，需有Springer访问权限（未测试）

### CHI_spider
可以批量爬取CHI会议的所有摘要，修改后也可以爬取其他会议。由于ACM的文章页面只有很少的id class，所以代码写的比较费解。BeautifulSoup + requests 速度较慢，好处是不会被封。

### Google_scholar_spider
可以在谷歌学术的搜索列表中爬取标题、作者、摘要等，但是摘要不完整

### Science_spider
用scrapy写，起始url列表需手动设置。爬取过程偶尔出现404，设置DOWNLOAD_DELAY = 2也没有改善，反爬虫措施有待加强

### Nature_spider
基于requests+bs，目前是爬取某一期的所有文章