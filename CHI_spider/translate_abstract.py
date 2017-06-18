import json
import requests
import hashlib
import json
import urllib
import random


def translate(query):
    appid = '1841de84b696ae86'
    secret_key = 'CWTn9rXAKaELYN0dYdks0vb3IEbGQuYM'
    from_lang = 'en'
    to_lang = 'zh_CHS'
    salt = random.randint(32768, 65536)
    sign = appid + query + str(salt) + secret_key
    m1 = hashlib.md5()
    m1.update(sign.encode())
    sign = m1.hexdigest()
    my_url = "https://openapi.youdao.com/api?"+'&q='+urllib.parse.quote(query)+'&salt='+str(salt)+'&sign='+sign+'&from='+str(from_lang)+'&appKey='+str(appid) + '&to=' + str(to_lang)
    try:
        r = requests.get(my_url)
        response = r.content
        json_data = json.loads(response)
        return json_data['translation']
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    file = 'CHI17.txt'
    with open(file) as f:
        all_abs = f.readlines()

    for i in range(1, len(all_abs)):
        all_abs[i] = eval(all_abs[i])

    for i in range(1, len(all_abs)):
        all_abs[i]['link'] = all_abs[i]['link'].split('&')[0]

    with open('CHI17_mkd.txt', 'w') as f:
        for i in range(1, len(all_abs)):
            f.write('### {}. '.format(str(i))+all_abs[i]['title']+'\n')
            f.write('*'+all_abs[i]['session']+'* \n\n')
            f.write(all_abs[i]['abstract']+'\n \n')
            f.write('>'+translate(all_abs[i]['abstract'])[0]+ '\n')
            print('{} articles ok'.format(str(i)))
            f.write('>[article link](' + all_abs[i]['link']+')\n \n')
