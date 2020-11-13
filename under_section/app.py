import requests
from bs4 import BeautifulSoup
import time
import re
import csv

URL = 'http://bazarpnz.ru/nedvizhimost/arenda_zhilja/posutochnaja_arenda/'


def get_html(url):
    """
    получаем HTML главной страницы сайта
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    r = requests.get(url, headers=headers)
    if r.ok:  # 200 - True, another 403, 404 - False
        return r.text
    else:
        print(r.status_code)


def get_rn_urls(html):
    url_list = []
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find('table', id="table_avto").find('tr')
    urls = tr.find_all('a')
    for url in urls:
        url_list.append(URL + (url.get('href')))

    return url_list


def get_rn_name(html):
    name_list = []
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find('table', id="table_avto").find('tr')
    urls = tr.find_all('a')
    for url in urls:
        name_list.append(url.text)

    return name_list


def get_billboards_url(html):
    billboards_list = []
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find_all('table', class_='list')[0].find_all('tr')

    for tr in trs:
        try:
            url = tr.find('td', class_='text').find('a').get('href')
            if 'i58' not in url:
                billboards_list.append('http://bazarpnz.ru' + url)
            else:
                billboards_list.append(url.split('?')[0])
        except:
            url = 'no url'

    return billboards_list


def pagination(url):
    while True:
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        try:
            pattern = 'следующей'
            url = 'http://bazarpnz.ru' + soup.find('td', class_='pages').find('a', text=re.compile(pattern)).get(
                'href')
            return url
        except:
            break


def all_area_urls(url):
    area_urls = []
    while True:
        try:
            html = get_html(url)
            area_urls.append(get_billboards_url(html))
            url = pagination(url)
        except:
            break
    all_area_urls = []

    for item in area_urls:
        for i in item:
            all_area_urls.append(i)

    return all_area_urls


def write_csv(data):
    with open('base.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['url'],
                         data['type'],
                         data['price'],
                         data['name'],
                         data['phone'],
                         data['mail'],
                         data['when'],
                         data['title'],
                         data['post'],
                         ))


def get_content(url):
    number = re.findall('\d+', url)
    if len(number) == 1:
        trueURL = 'http://bazarpnz.ru/tofile.php?id=' + str(number[0])
    else:
        trueURL = 'http://bazarpnz.ru/tofile.php?id=' + str(number[1])

    r = requests.get(trueURL)
    page = r.text

    soup = BeautifulSoup(page, 'lxml')
    # Заголовок объявления
    try:
        title = soup.find('h2').text
    except:
        title = 'No Title'
    try:
        paragraph = soup.find_all('p')
    except:
        paragraph = 'No P'
    # Тип объявления Покупка Продажа
    try:
        tipe1 = paragraph[1].text.split()[2]
        tipe = tipe1.replace(' ', '')
    except:
        tipe = 'No Type'

    try:
        string = paragraph[2].text
        str_price = string.split('руб')[0]
        a = re.findall('\d+', str_price)
        price = int(''.join(map(str, a)))

    except:
        price = 'No Price'

    try:
        post = paragraph[4].text
    except:
        post = 'NoPost'
    try:
        contacts = paragraph[6].text
        string = contacts.split('\n\t')
    except:
        string = 'No Contacts'
    try:
        name = string[1].split(': ')[1].replace('"', '')
    except:
        name = 'NoName'
    try:
        phone = string[2].split(': ')[1].replace('\n', '')
    except:
        phone = 'NoPhone'
    try:
        mail = string[3].split(': ')[1].replace('\n', '')
    except:
        mail = 'NoMail'
    try:
        when_string = paragraph[7].text.split(': ')
        when = when_string[1]
    except:
        when = 'No Date'

    data = {'url': url,
            'type': tipe,
            'price': price,
            'name': name,
            'phone': phone,
            'mail': mail,
            'when': when,
            'title': title,
            'post': post,
            }

    try:
        write_csv(data)
    except:
        print('Write Wrong')

    time.sleep(2)


def main():
    html = get_html(URL)
    urls = get_rn_urls(html)
    count = 0
    for url in urls:
        print(get_rn_name(get_html(url))[count])
        with open('base.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([get_rn_name(get_html(url))[count]])
        count += 1
        for item in all_area_urls(url):
            get_content(item)


if __name__ == '__main__':
    main()
