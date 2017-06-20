import requests
import hashlib
import json
import urllib
import random


def translate(q):
    appid = '20170618000059135'
    secretKey = 'utIzHnjpeWSntf8CvnlM'
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
