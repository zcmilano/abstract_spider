from bs4 import BeautifulSoup
import re
import string
import requests
import hashlib
import json
import urllib
import random
# 首先导入需要的模块

# 然后定义获取HTML内容的函数
def getHTMLText(url, code='utf-8'):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
        r = requests.get(url, headers = headers)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ''

# 这段代码是从网上找的，用来对HTML进行初步清洗，以防使用soup.sibling()的时候出现空白
def bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)  # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)  # convert newlines to spaces
    # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html)  # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html)  # remove whitespaces after closing tags
    return html

# 定义寻找会议名称以及地点的函数，并且替换字符串中不适合做文件名的符号
def conference_name(soup):
    name = soup.find_all('table', class_='medium-text')[4].get_text()
    exclude = set(string.punctuation)
    name = ''.join(ch for ch in name if ch not in exclude)
    return ''.join(name.split())

# 下面这几个函数可能会有些费解，因为爬取网页中的id或者class很少，所以只能根据其他的属性判断内容

# session是会议中的分主题，一个session下会有若干文章，以下函数判断一个session中有几篇文章
def how_much_articles(soup):
    i = 0
    try:
        soup = soup.next_sibling
        while not is_session(soup):
            if is_title(soup):
                soup = soup.next_sibling
                i += 1
            else:
                soup = soup.next_sibling
    except:
        print('last session')

    return i

# 判断一个标签的内容是不是session
def is_session(soup):
    try:
        if soup.find('td', colspan='2'):
            return True
    except:
        return False

# 判断一个标签是不是包含文章标题
def is_title(soup):
    try:
        if soup.find('td', colspan='1'):
            return True
        else:
            return False
    except:
        return False

# 判断一个标签是不是包含文章摘要
def is_abstract(soup):
    try:
        if soup.find('span', id=True):
            return True
        else:
            return False
    except:
        return False

# 提取标签中的文章标题
def find_title(soup):
    try:
        return soup.find('a').text
    except:
        print('where is the title???????????????????????????????????')
        return 'can not find title'

# 提取文章标题中的原文链接
def find_link(soup):
    try:
        return 'https://dl.acm.org/' + soup.find('a')['href']
    except:
        print('can not find link')
        return 'can not find link'

# 以列表的形式提取作者
def find_author(soup):
    authors = []
    for author in soup.find_all('a'):
        authors.append(author.text)
    return authors

# 提取文章的页码
def find_pages(soup):
    try:
        return soup.find('span').text[7:]
    except:
        print('can not find pages')
        return 'can not find pages'

# 提取文章的摘要
def find_abstract(pages_soup):
    try:
        pages_soup.find('span', id=re.compile("toHide")).get_text()
    except:
        return ''

# 定义翻译函数，调用百度翻译的API，appid和secret_key请自行申请（免费的）
def translate(q):
    appid = 'your_appid'
    secretKey = 'your_secretKey'
    my_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode())
    sign = m1.hexdigest()
    my_url = my_url + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        r = requests.get(my_url)
        response = r.content
        json_data = json.loads(response)
        return json_data['trans_result'][0]['dst']
    except Exception as e:
        return str(e)

# 以下就是主函数了，输入会议的url，输出内容的Markdown
def download_proceedings(url):
    html = getHTMLText(url, code='utf-8')
    html = bs_preprocess(html)
    # 建立soup
    soup = BeautifulSoup(html, 'html.parser')
    print('soup ok')
    file_name = conference_name(soup)[24:]
    # 寻找文章的列表
    articles_table = soup.find_all(class_="text12")[1]
    print('articles_table ok')
    session_tds = articles_table.find_all('td', colspan='2')
    article_tds = articles_table.find_all('td', colspan='1')
    session_num = len(session_tds)
    article_num = len(article_tds)
    print('{}sessions {}articles'.format(str(session_num), str(article_num)))
    articles = []

    article_from = 0
    # 早期的年份没有session，所以增加if判断，session为零就直接下载文章
    if session_num:
        for i in range(session_num):
            abstract_steps = i+2
            session_name = session_tds[i].parent.get_text()
            num_of_articles = how_much_articles(session_tds[i].parent)
            article_to = article_from + num_of_articles
            for i in range(article_from, article_to):
                article_info = {}
                title_tr = article_tds[i].parent
                article_info['session'] = session_name
                article_info['title'] = find_title(title_tr)
                article_info['link'] = find_link(title_tr)
                #print('title and link found')
                article_info['author'] = find_author(title_tr.next_sibling)
                article_info['pages'] = find_pages(title_tr.next_sibling.next_sibling)
                try:
                    article_info['abstract'] = soup.find('span', id='toHide{}'.format(str(i + abstract_steps))).get_text()
                except:
                    article_info['abstract'] = 'can not find Abstract'
                    print('can not find abstract')
                articles.append(article_info)
                print('{} article{} finish'.format(session_name, str(i+1)))
                article_from = article_to
    # 有session的会议中，第一个标签一定是session，然后判断此session有几篇文章，借此确定文章列表的索引范围，依次迭代
    else:
        for i in range(article_num):
            article_info = {}
            title_tr = article_tds[i].parent
            article_info['title'] = find_title(title_tr)
            article_info['link'] = find_link(title_tr)
            #print('title and link found')
            article_info['author'] = find_author(title_tr.next_sibling)
            article_info['pages'] = find_pages(title_tr.next_sibling.next_sibling)
            try:
                article_info['abstract'] = soup.find('span', id='toHide{}'.format(str(i + 1))).get_text()
            except:
                article_info['abstract'] = 'can not find Abstract'
                print('can not find abstract')
            articles.append(article_info)
            print('article{} finish'.format(str(i+1)))

    with open("{}.md".format(file_name), "w") as f:
        for i in range(len(articles)):
            f.write('### {}. '.format(str(i+1))+articles[i]['title']+'\n')
            f.write('*'+articles[i]['session']+'* \n\n')
            f.write(articles[i]['abstract']+'\n \n')
            f.write('>'+translate(articles[i]['abstract'])[0]+ '\n')
            f.write('>[article link](' + articles[i]['link']+')\n \n')



if __name__ == '__main__':
    url_list = ['https://dl.acm.org/citation.cfm?id=3025453&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=2858036&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=2702123&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=2556288&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=2470654&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=2207676&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1978942&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1753326&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1518701&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1357054&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1240624&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1124772&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1054972&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=985692&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=642611&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=507752&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=503376&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=365024&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=332040&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=302979&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=286498&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=274644&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=258549&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=257089&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=238386&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=223355&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=223904&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=259963&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=191666&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=169059&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=259964&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=142750&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=1125021&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=108844&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=97243&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=67449&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=57167&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=29933&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=22627&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=317456&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=800045&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=800049&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=800276&preflayout=flat',
                'https://dl.acm.org/citation.cfm?id=800275&preflayout=flat']
    for url in url_list:
        download_proceedings(url)
