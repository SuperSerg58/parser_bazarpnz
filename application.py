import requests
from bs4 import BeautifulSoup
import time
import re
import csv


def get_main_html(url):
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


def get_main_data(html):
    """
    получаем ссылки на все разделы и записываем их в файл, а так же в список.
    """
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find('table', id="table_rub").find_all('tr')[1]
    td = trs.find_all('td')[0]
    items = td.find_all('a')
    url_list = []  # Записываем все ссылки разделы объявления в список.
    for item in items:
        url = 'http://bazarpnz.ru/' + item.get('href') + '\n'
        url_list.append(url)
        file = open('url.txt', 'a')
        file.write(url)
        file.close()

    return url_list


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
    trueURL = 'http://bazarpnz.ru/tofile.php?id=' + str(number[0])

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


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    r = requests.get(url, headers=headers)
    if r.ok:  # 200 - True, another 403, 404 - False
        return r.text
    else:
        print(r.status_code)


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find_all('table', class_='list')[0].find_all('tr', class_='norm')

    for tr in trs:
        try:
            url = 'http://bazarpnz.ru' + tr.find('td', class_='text').find('a').get('href')
        except:
            url = 'no url'

        if 'ann' in url:
            print(url)
            get_content(url)
            file = open('all_url.txt', 'a')
            file.write(url + '\n')
            file.close()


def main():
    mainUrl = 'http://bazarpnz.ru/'
    html = get_main_html(mainUrl)

    for url in get_main_data(html):

        while True:
            html = get_html(url)
            get_page_data(html)

            soup = BeautifulSoup(html, 'lxml')
            try:
                pattern = 'следующей'
                url = 'http://bazarpnz.ru' + soup.find('td', class_='pages').find('a', text=re.compile(pattern)).get(
                    'href')
                print(url)
            except:
                break


if __name__ == '__main__':
    main()
