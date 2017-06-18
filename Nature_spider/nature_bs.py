import requests
from bs4 import BeautifulSoup


def get_html_text(url, code='utf-8'):

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ''


def find_articles_link(url):
    html = get_html_text(url, code='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', id='content')
    links = []
    for i in content('article'):
        link = i.find('a')['href']
        if link[:4] == 'http':
            links.append(link)
        else:
            links.append('http://www.nature.com' + link)
    return links


def find_article_info(url):
    html = get_html_text(url, code='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    article_info = {}
    try:
        article_info['title'] = soup.find('h1', class_='article-heading').text
    except:
        article_info['title'] = 'can not find title'
    try:
        article_info['author'] = soup.find('ul', class_='authors citation-authors').find('a').text
    except:
        article_info['author'] = 'can not find author'
    try:
        article_info['abstract'] = soup.find('div', id='abstract').find('p').text
    except:
        article_info['abstract'] = 'can not find abstract'

    try:
        article_info['affliation'] = soup.find('div', id='author-affiliations').find('h3').text
    except:
        article_info['affliation'] = 'can not find affliation'

    return article_info

if __name__ == '__main__':
    start_url = 'http://www.nature.com/nature/journal/v546/n7657/index.html'
    all_articles = []
    links = find_articles_link(start_url)
    file_name = 'test'
    for link in links:
        article_info = find_article_info(link)
        all_articles.append(article_info)


    with open("{}.txt".format(file_name), "w") as f:
        f.write(str(len(all_articles)) + '\n')
        for article in all_articles:
            f.write(str(article) + '\n')