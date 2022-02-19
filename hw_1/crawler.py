import encodings
import re
import zipfile

import requests


def index_txt(links):
    f_index = open("index.txt", "w")
    pattern = "%d. %s\n"
    for i in range(len(links)):
        f_index.write(pattern % (i, host + links[i]))
    f_index.close()


def vykachka_zip(content):
    i = 0
    with zipfile.ZipFile('vykachka.zip', 'w') as f:
        for page in content:
            f.writestr("page" + str(i) + ".html", page.encode('ascii', errors='xmlcharrefreplace'))
            i += 1


def find_links(content):
    prefix = "http://bigkarta.ru"
    links_regex = "href=[\"\']http://bigkarta.ru(.*?)[\"\']"
    links = re.findall(links_regex, content)
    print(links_regex)
    print(links)
    return list(
        map(lambda e: prefix + e, filter(lambda e: not str(e).endswith((".jpg", ".png", ".ogg")), links)))


def open_url(url):
    r = requests.get(url)
    print(r.status_code)
    r.encoding = r.apparent_encoding
    if r.status_code == 200:
        return r.text
    else:
        return None


if __name__ == '__main__':
    host = 'http://bigkarta.ru'
    start_url = 'http://bigkarta.ru/strany.htm'
    start_page = open_url(start_url)
    print(start_page)
    links = find_links(start_page)
    print(links)
    links = links[:130]

    index_txt(links)
    links_content = []
    for link in links:
        content = open_url(link)
        if content is not None:
            print(content)
            links_content.append(content)

    vykachka_zip(links_content)
