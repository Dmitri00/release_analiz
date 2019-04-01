import requests
import urllib.parse as urlparse
from config import google_search_url, google_search_params
from bs4 import BeautifulSoup
import threading
import random

class PagerError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
class ResulterError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
class GooglePager:
    def __init__(self, html_page, pass_first=True):
        self.url_base = 'https://www.google.com'
        self.base_page = BeautifulSoup(html_page,'html.parser')
        self.nav_table = self.base_page.find(id='nav')
        if self.nav_table != None:
            a_tags_pagination = self.nav_table.findAll('a')[:-1]
        else:
            a_tags_pagination = []

        a_tags = a_tags_pagination
        p_tag = self.base_page.find(id='ofr')
        if p_tag != None:
            a_tag_hidden = p_tag.findAll('a')
            if a_tag_hidden != None:
                print(a_tag_hidden)
                a_tags.append(a_tag_hidden[0])
                print('Просмотр скрытых результатов')
        self.page_urls = iter(map(lambda x: self.url_base + x.attrs['href'], a_tags))

    def __iter__(self):
        return self.page_urls
    def __next__(self):
        if self.page_num < self.depth:
            next(self.page_urls)
        else:
            raise StopIteration

class GoogleResultGen:
    def __init__(self, html_page):
        self.url_base = 'https://www.google.com'
        try:
            self.base_page = BeautifulSoup(html_page,'html.parser')
            href_blocks = self.base_page.findAll(class_='r')
            if len(href_blocks) == 0:
                raise ResulterError()
            self.hrefs = list(map(lambda x: x.find('a').attrs['href'], href_blocks))
            def tryconvert(href):
                try:
                    return urlparse.parse_qs(href)['/url?q'][0]
                except KeyError:
                    return ''
            self.urls = iter(map(tryconvert, self.hrefs))
            #print(self.urls)
            #self.urls = iter(map(lambda x: self.url_base + x.find('a').attrs['href'], self.base_page.findAll(class_='r')))
            #self.page_num = 0
            #self.depth = len(self.base_page.findAll('g'))
        except TypeError:
            self.urls = iter([])
    def __iter__(self):
        return self.urls
    def __next__(self):
        next(self.urls)
class BaiduPager:
    def __init__(self, html_page, pass_first=True):
        self.url_base = 'https://www.baidu.com'
        self.base_page = BeautifulSoup(html_page,'html.parser')
        self.nav_table = self.base_page.find(id='page')
        if self.nav_table != None:
            a_tags_pagination = self.nav_table.findAll('a')[:-1]
        else:
            a_tags_pagination = []

        a_tags = a_tags_pagination
        # Поиск скрытых результатов
        p_tag = self.base_page.find(id='ofr')
        if p_tag != None:
            a_tag_hidden = p_tag.findAll('a')
            if a_tag_hidden != None:
                print(a_tag_hidden)
                a_tags.append(a_tag_hidden[0])
                print('Просмотр скрытых результатов')
        self.page_urls = iter(map(lambda x: self.url_base + x.attrs['href'], a_tags))

    def __iter__(self):
        return self.page_urls
    def __next__(self):
        if self.page_num < self.depth:
            next(self.page_urls)
        else:
            raise StopIteration

class BaiduResultGen:
    def __init__(self, html_page):
        self.url_base = 'https://www.google.com'
        try:
            self.base_page = BeautifulSoup(html_page,'html.parser')
            href_blocks = self.base_page.findAll(class_='result')
            if len(href_blocks) == 0:
                raise ResulterError()
            self.hrefs = list(map(lambda x: x.find('a').attrs['href'], href_blocks))
            def tryconvert(href):
                try:
                    return urlparse.parse_qs(href)['/url?q'][0]
                except KeyError:
                    return ''
            # У Baidu в теге <a> стоит полная липовая ссылка на сайт
            self.urls = iter(self.hrefs)
            #print(self.urls)
            #self.urls = iter(map(lambda x: self.url_base + x.find('a').attrs['href'], self.base_page.findAll(class_='r')))
            #self.page_num = 0
            #self.depth = len(self.base_page.findAll('g'))
        except TypeError:
            self.urls = iter([])
    def __iter__(self):
        return self.urls
    def __next__(self):
        next(self.urls)

class RequestGenerator:
    def __init__(self, text,title='', hero='', institute=''):
        self.requests = []
        if hero != '' and institute != '':
           self.requests.append(hero +' '+institute) 
        self.text = text.split('.')
        random.shuffle(self.text)
        self.requests.append(self.text)
        self.requests = iter(self.requests)
        self.current_ = 0
    def __iter__(self):
        return self
    def __next__(self):
        try:
            sentence = next(self.requests)
            while len(sentence) <= 10:
                sentence = next(self.requests)
        except StopIteration:
            raise StopIteration
        #return sentence
        request = '\"{}\"'.format(sentence.strip())
        return request


proxies = {'http':'1.10.187.118:62000', 'https':'http://54.39.209.38:3128'}

headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cookie':'CGIC=AWwwwege; NID=; 1P_JAR=2019-03-13-10; SID=sAfW; HSID=; SSID=; APISID=; SAPISID=; SIDCC=; _gcl_au=; ANID=OPT_OUT; OGPC=:; DV=AAwFgfsdf'}

def RoundRobin(buff):
    while True:
        for elem in buff:
            yield elem
user_agents = ['Chomre','Mozilla/5.0','Opera','python-requests']
proxies_list = ['1.10.188.252:8080',None,'1.179.151.145:45824','1.179.151.145:45824','1.20.100.133:46755',
        '1.2.169.34:8080','1.10.187.118:62000','1.10.186.153:32731','191.7.198.202:8080','95.64.253.177:30002']
proxies_gen = RoundRobin(proxies_list)
agents_gen = RoundRobin(user_agents)
class Downloader:
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.timer = self.invoke_timer(0.1) 
        self.timer.start()
    def invoke_timer(self, timeout):
        return threading.Timer(timeout, lambda : None)
    def fuzzy(self):
        headers['Cookie'] = headers['Cookie']+'A'
        if random.random() < 0.5:
            proxies['https']=next(proxies_gen)
        else:
            headers['User-Agent'] = next(agents_gen)

    def big_timeout(self):
        self.timer = self.invoke_timer(3*self.timeout)
        self.timer.start()
    def download(self, url, use_proxy=False,use_agent=True,default_agent=False, timeout=5):
        while self.timer.isAlive():
            pass
        session = requests.Session()
        if use_proxy:
            session.proxies = proxies
        try:
            if use_agent:
                if default_agent:
                    headers['User-Agent']='Mozilla/5.0'
                page = session.get(url, headers=headers,timeout=timeout)
            else:
                page = session.get(url, timeout=timeout)
            if page.encoding == None:
                return None
        except ConnectionError:
            proxies['https'] = next(proxies_gen)
            return None
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        self.timer = self.invoke_timer(self.timeout)
        self.timer.start()
        if page.status_code == 200:
            return page.text
        else:
            return None
def build_url_request(phrase):
    search_params = google_search_params.copy()
    search_params['q'] = phrase 
    search_url = google_search_url.format(urlparse.urlencode(search_params))
    print(search_url)
    return search_url


    
class Searcher:
    def __init__(self, article, search_engine_name='google', search_depth=3):
        if article == '':
            raise ArgumentError('Search phrase is empty')
        self.supported_engines = ['google']
        if search_engine_name not in self.supported_engines:
            raise ValueError('Search engine %s is not supported' % search_engine_name)
        self.search_engine_name = search_engine_name
        self.keyword_builder = RequestGenerator(article)
        self.downloader = Downloader()
        self.search_depth = search_depth
    def start_request(self, phrase):
        try:
            search_url = build_url_request(phrase)
            print(search_url)
            i = 0
            retry_count = 5
            page = self.downloader.download(search_url, use_proxy=False)
            while page == None and i < retry_count:
                page = self.downloader.download(search_url)
                i+=1
            if i == retry_count:
                raise Exception('Cannot get data by url {}'.format(search_url))
            #print(page)
            return page
        except StopIteration:
            raise StopIteration    
    def gen(self):
        for phrase in self.keyword_builder:
            print('-----------------')
            print(phrase)
            phrase_score = 10
            try:
                first_page = self.start_request(phrase)
                #print(first_page)
                try:
                    resulter = GoogleResultGen(first_page)
                except Exception:
                    continue
                for result in resulter:
                    if result.startswith('http'):
                        yield result
                other_pages_url = GooglePager(first_page)
                for i,page_url in enumerate(other_pages_url):
                    #phrase_score +=5
                    if i >= self.search_depth:
                        break
                    html_page = self.downloader.download(page_url)
                    for result in GoogleResultGen(html_page):
                        #page_score += yield result
                        if result.startswith('http'):
                            yield result
                        #if score <= -10:
                            #break
                            #phrase_score -=10
                    #if phrase_score <= -20:
                    #    break
                    
            except PagerError:
                print('Ошибка чтения результатов поиска')
            except ResulterError:
                print('Гугл заблокировал бота. Поиск будет возобновлен после перерыва в 5-15 секунд')
                self.downloader.fuzzy()
                self.downloader.big_timeout()

            
    
