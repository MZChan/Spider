# -*- coding:utf-8 -*-

import requests
from requests import RequestException
from bs4 import BeautifulSoup
import re
import time
from random import randrange
import threading
import os
from concurrent.futures import ThreadPoolExecutor


site_url = 'http://cl.nd77.pw/'
base_url = 'http://cl.nd77.pw/thread0806.php?fid=8&search=&page='

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
}


def getsublink(url):
    link_list = {}
    response = requests.get(url, headers=headers)

    try:
        response.encoding = response.apparent_encoding      #
        soup = BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.ConnectionError:
        pass

    url_pattern = 'htm_data.*html'
    title_pattern = '\">.*</a'
    re.compile(url_pattern)
    re.compile(title_pattern)

    for tp in soup.select('tr'):

        # if u'美' in tp.text:
        for raw_link in tp.select('h3'):
            try:
                titles = re.search(title_pattern, str(raw_link))
                urls = re.search(url_pattern, str(raw_link))
                link_list[titles.group().strip(
                    '\">').strip('</a')] = urls.group()

            except AttributeError:
                pass

    return link_list


def getimglink(link_list):
    for title in link_list:
        url = site_url + link_list[title]
        img_url = []
        print 'current url', url

        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.ConnectionError:
            pass

        for item in soup.select('input'):
            try:
                pattern = 'src=".*jpg'
                re.compile(pattern)
                img_src = re.search(pattern, str(item))
                tmp = str(img_src.group()).replace('src=\"', '')
                img_url.append(tmp)
            except AttributeError:
                pass

        args = []
        with ThreadPoolExecutor(20) as executor:
            for item in img_url:
                args.append([item, title])
            executor.map(download, args)

        # for item in img_url:
        #     args = [item, title]
        #     t = threading.Thread(target=download, args=args)
        #     t.start()
        #     t.join()


def download(args_list):
    img_url = args_list[0]
    title = args_list[1]
    filename = str(img_url).split('/')[-1]
    print img_url, filename
    path = '/media/stan/Ubuntu/girl_multi_thread/' + title
    if not os.path.exists(path):
        os.mkdir(path)
    elif os.path.exists(path + '/' + str(filename)):
        print 'file exists, return'
        return

    try:
        response = requests.get(img_url, headers=headers, timeout=5)
        if response.status_code == 200:
            print 'path, filename', path, str(filename)
            with open('%s/%s' % (path, str(filename)), 'wb') as f:
                f.write(response.content)
                f.close()
                print 'write ok!'
    except BaseException:
        print 'we have a bad url', img_url
        return 'ERR'


if __name__ == '__main__':
    start = time.time()

    for i in range(1, 100):
        getimglink(getsublink(base_url + str(i)))
    end = time.time()
    print end - start
