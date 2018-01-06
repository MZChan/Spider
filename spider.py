# -*- coding:utf-8 -*-

import requests
import re
import time
import random
import sys
from Agents import user_agents
from bs4 import BeautifulSoup
from pymongo import MongoClient
from requests.exceptions import RequestException


class Spider:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['magnet-link']
        self.link = self.db['link']
        self.seed = self.db['seed']
        self.base_url = 'http://www.javbus84.com/liuyi/julia_1.html'
        self.pages = 34
        self.header = random.choice(user_agents)

    def get_html(self, url):
        try:
            r = requests.get(url, self.header, timeout=5)

            if r.status_code == 200:
                r.encoding = r.apparent_encoding
                return r.text
            else:
                print 'bad request, error code:', r.status_code
                return
        except RequestException as e:
            print e.message

    def get_sublink(self, html):

        soup = BeautifulSoup(html, 'lxml')
        data = soup.select('.row')
        print soup.select('div')
        for item in data:
            # print item
            try:
                pattern = re.compile('href="(.*)" target=.*?title="(.*)">')
                if len(re.findall(pattern, str(item))) > 0:
                    url, title = re.findall(pattern, str(item))[0]
                    size = re.search('size">(.*)<', str(item)).group()
                    post = {
                        'url': url,
                        'title': title,
                        'size': size
                    }
                    print 'saving link', url
                    if not self.link.find_one({'url': url}):
                        self.link.save(post)
                    else:
                        print 'link exists, pass'

            except AttributeError as e:
                print e

    def get_magnet(self, link):
        header = random.choice(user_agents)

        try:
            r = requests.get(link['url'], header, timeout=5)
            if r.status_code == 200:
                r.encoding = r.apparent_encoding
                soup = BeautifulSoup(r.text, 'lxml')

                try:
                    pattern = 'readonly="">magnet.*?</textarea>'

                    magnet = re.search(pattern, str(soup.select('textarea')))

                    seed = magnet.group().replace('readonly="">', '').replace('</textarea>', '')

                    post = {
                        'title': link['title'],
                        'magnet': seed,
                        'size': link['size']
                    }
                    print 'title', link['title'], 'magnet', seed, 'size', link['size']
                    if not self.seed.find_one({'magnet': seed}):
                        self.seed.save(post)
                        print 'save to mongodb success!'
                    else:
                        print 'sublink exists, pass!'
                except AttributeError:
                    print 'we have a AttributeError, pass'
        except RequestException as e:
            print e.message


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    s = Spider()
    if s.get_html(s.base_url):
        s.get_sublink(s.get_html(s.base_url))

    for i in s.link.find():
        if not s.seed.find_one({'title': i['title']}):
            s.get_magnet(i)
            time.sleep(3)
        else:
            print 'link already crawled, getting next.'

