import readability
import nltk, string
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
from similarity.cosine import Cosine
from similarity.ngram import NGram
from similarity.metric_lcs import MetricLCS
from HtmlCleaner import HtmlCleaner
import urllib.parse as urlparse
import re

MAX_PAGE_SCORE = 10.0
PAGE_NECESSARY_SCORE = 1.99
PAGE_SUFFICIENT_SCORE = 7.0
PAGE_MAX_SCORE = 10.0 
PAGE_HIT_SCORE = 1.0
PAGE_TITLE_COST = 5.0
PAGE_TEXT_COST = 5.0
PAGE_DIRECTLINK_COST = 10.0
PAGE_DOI_COST = 10.0

class ResultDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.hit_score = PAGE_HIT_SCORE 
        self.filter_score = PAGE_NECESSARY_SCORE
        self.max_score = PAGE_MAX_SCORE
        self.texts = {}

    def hit(self,url, text):
        if url in self.keys():
            self[url] = min(self[url]+self.hit_score, self.max_score)
        else:
            self[url] = 1
            self.texts[url] = text
        return self[url]
    def add_score(self, url, score):
        self[url] = min(self[url]+score,self.max_score)
        return self[url]
    def filter(self):
        results = []
        for url, score in self.items():
            if score >= self.filter_score:
                results.append((url,score))
        return results
    def contains(self,url,text):
        parsed_1url = urlparse.urlparse(url)
        netloc1 = parsed_1url.netloc
        hash1 = hash(netloc1+text)
        contains = False
        for url in self.keys():
            parsed_2url = urlparse.urlparse(url)
            netloc2 = parsed_2url.netloc
            hash2 = hash(netloc2 + self.texts[url])
            if hash1 == hash2:
                contains = True
                break
        return contains
    def get_dublicate(self,url,text):
        parsed_1url = urlparse.urlparse(url)
        netloc1 = parsed_1url.netloc
        hash1 = hash(netloc1+text)
        contains = False
        for url in self.keys():
            parsed_2url = urlparse.urlparse(url)
            netloc2 = parsed_2url.netloc
            hash2 = hash(netloc2 + self.texts[url])
            if hash1 == hash2:
                return url


class Page:
    def __init__(self,url,html):
        self.url = url
        self.html = html
        self.txt_cleaner = HtmlCleaner()
        success = False
        for i in range(3):
            try:
                readable_article = readability.Document(html)
                title, article_html = readable_article.title(),readable_article.summary()
                self.article_html = self.txt_cleaner.clean_html(article_html)
                self.article_text = self.article_html
                self.title = title
                success = True
            except Exception as e:
                print(e)
                self.title = try_extract_title(url)
                self.article_html = None
                self.article_text = ''
        if not success:
             print('Произошла ошибка при обработке страницы. Будет обработан только URL-адрес страницы.')

class ReferencePage:
    def __init__(self,title,text,url,hero='',institute='',doi=''):
        self.title = title
        self.article_text = text
        self.url = url
        self.hero = hero
        self.institute = institute
        self.doi = doi
    
def clean_url(url):
    return url
    assert url.startswith('http')
    return url.split(':')[1] 
def restore_url(url):
    return url
    return 'http:'+url
def try_extract_title(url):
    path = urlparse.urlparse(url).path.rsplit('/',1)[-1]
    path = path.replace(' ','')
    path = path.replace('-',' ')
    path = path.replace('_',' ')
    return path

class Analyzer:
    def __init__(self, title,text,url_,hero='',institute='',doi=''):
        url = clean_url(url_)
        self.reference = ReferencePage(title,text,url,hero,institute,doi)
        self.results = ResultDict() 
        self.blacklist = {}
        self.metadata = {}
        
        self.hero_inst_re = re.compile('(?={})(?={}).{}'.format(self.reference.institute,self.reference.hero,'{1,100}'))
        self.article_url_re = re.compile(url)
        self.doi_re = re.compile(self.reference.doi)

    def analyze(self, url_,html):
        url = clean_url(url_)
        if url == '' or url == None:
            return -1.0
        score = 0.0
        if url in self.blacklist:
            return score

        page = Page(url,html)
        dublicate_url = self.results.get_dublicate(url,page.article_text)
        if dublicate_url != None:
            url = dublicate_url
            assert url in self.results
        if  url in self.results and self.results[url] > PAGE_SUFFICIENT_SCORE:
            return self.results[url]

        if page.article_text != None and len(page.article_text) <= 50000 or 'pdf' in url :
            
            score = self.compute_score(page)

            if score > PAGE_NECESSARY_SCORE:
                if page.url not in self.metadata:
                    page.html = None
                    page.article_html = None
                    page.article_text = None
                    self.metadata[page.url] = page

        return float(score)
        


    def compute_score(self,page):
        score = 0.0
        
        if score >= PAGE_SUFFICIENT_SCORE:
            return score
        if 'pdf' in page.url:
            #assert score != 0.0
            return score
        score = self.results.hit(page.url,page.article_text)
        if page.title == None:
            return score
        if self.direct_link_rule(page):
            score = self.results.add_score(page.url,self.results.max_score)
            print('Найдена прямая url-ссылка на источник')
            return self.results.max_score


        if self.doi_rule(page):
            score = self.results.add_score(page.url,self.results.max_score)
            print('Найдена прямая doi-ссылка на источник')
            return self.results.max_score

        #article_text = self.txt_cleaner.clean_txt(article_html)
        try:
            title_similarity = self.title_similarity(page)
            text_similarity = self.cite_rule(page)
        except Exception:
            text_similarity = 0.0
            title_similarity = self.title_similarity(page)
            score = title_similarity*PAGE_TITLE_COST
            return score
        cite_score = PAGE_TITLE_COST*text_similarity + PAGE_TITLE_COST*title_similarity
        score = self.results.add_score(page.url,cite_score)
        #print('Оценка близости текста {}'.format(cite_score))

        if self.hero_institute_rule(page):
            score = self.results.add_score(page.url,cite_score)
            print('Обнаружено упоминание героев публикации')
        return float(score)

    def direct_link_rule(self, page):
        if page.html  == None or page.html == '':
            return False
        all_links = BeautifulSoup(page.html, 'html.parser').findAll('a')
        def tryconvert(a_tag):
            try:
                return a_tag.attrs['href']
            except KeyError:
                return ''
        hrefs = iter(map(tryconvert, all_links))
        for href in hrefs:
            if self.article_url_re.search(href)!=None:
                return True
        return False

    def hero_institute_rule(self,page):
        if page.html == None or page.html == '':
            return False
        return self.reference.hero != '' and self.reference.institute != '' and self.hero_inst_re.search(page.article_html) != None
    def doi_rule(self,page):
        if page.html == None or page.html == '':
            return False
        return self.reference.doi != '' and self.doi_re.match(page.article_html) != None
    def cite_rule(self,page):
        try:
            #ngram = self.fourgram(self.article,text)
            #print('Оценка точности по принципу н-грамм:{}',ngram)
            s1 = self.reference.article_text
            s2 = page.article_text
            cosine_char = self.cosine(s1,s2)
            #print('Оценка точности по принципу косинуса между векторами символов:{}',cosine_char)
            cosine_word = text_similarity(s1,s2) 
            #print('Оценка точности по принципу косинуса между векторами слов:{}',cosine_word)
            mean = (cosine_char+cosine_word)/2
            #print('Среднее - {}'.format(mean))
        except ZeroDivisionError:
            mean = 0
        return mean 

    def cosine(self, s0,s1):
        cosine = Cosine(15)
        p0 = cosine.get_profile(s0)
        p1 = cosine.get_profile(s1)
        #print('Cosine similarity \"%\" vs \"%\"'% (s0,s1))
        return cosine.similarity_profiles(p0, p1)

    def fourgram(self, s0,s1):
        fourgram = NGram(3)
        #print('Fourgram similarity \"%\" vs \"%\"'% (s0,s1))
        return 1 - fourgram.distance(s0, s1)
    def title_similarity(self,page):
        try:
            s1 = normalize(self.reference.title)
            s2 = normalize(page.title)
            n = 3
            p1_trigrams = Counter(nltk.ngrams(s1, n))
            p2_trigrams = Counter(nltk.ngrams(s2, n))
            p1_grams = Counter(nltk.ngrams(s1, 1))
            p2_grams = Counter(nltk.ngrams(s2, 1))
            cosine = Cosine(1)
            similarity = cosine.similarity_profiles(p1_trigrams,p2_trigrams)
            similarity = cosine.similarity_profiles(p1_grams,p2_grams)
            similarity = similarity / 2
            
        except ZeroDivisionError:
            similarity = 0
        return similarity

        #metric = MetricLCS()
        #return 1 - metric.distance(s1,s2)

    def get_results(self):
        page_scores = self.results.filter()
        results = []
        for url,score in page_scores:
            try:
                page = self.metadata[url]

                results.append((restore_url(url),page.title,float(score)))
            except KeyError:
                pass

        return results 

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
def text_similarity(text1,text2):
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    tfidf = vectorizer.fit_transform([text1,text2])
    return ((tfidf * tfidf.T).A)[0,1]
