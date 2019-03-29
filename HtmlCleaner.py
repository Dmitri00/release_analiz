import readability

import re


stop_words_re = '\s(a|about|above|after|again|against|all|am|an|and|any|are|aren\'t|as|at|be|because|been|before|being|below|between|both|but|by|can\'t|\
cannot|could|couldn\'t|did|didn\'t|do|does|doesn\'t|doing|don\'t|down|during|each|few|for|from|further|had|hadn\'t|has|hasn\'t|have|haven\'t|having|he|he\'d|he\'ll|\
he\'s|her|here|here\'s|hers|herself|him|himself|his|how|how\'s|i|i\'d|i\'ll|i\'m|i\'ve|if|in|into|is|isn\'t|it\'s|its|itself|let\'s|me|more|most|mustn\'t|my|myself|no|\
nor|not|of|off|on|once|only|or|other|ought|our|ours|the|so)\s+'
def clean_text(text):
    clean_text = text.lower()
def clean(html):
    cleaner = HtmlCleaner()
    return cleaner.clean()

class HtmlCleaner:
    def __init__(self):
        self.html_clean_rules = ['[\n\t]','<\s?figure[^>]*>.*</\s?figure[^>]*>', '(</?[^>]*>|&#?([a-z]|\d){1,4};)']
        self.txt_clean_rules = [stop_words_re,'[^a-z^A-Z^\s]', '\s[a-zA-Z]{1}\s', '\s+']
        self.html_rexps = iter(map(re.compile,self.html_clean_rules))
        self.txt_rexps = iter(map(re.compile,self.txt_clean_rules))
        
    
    def clean_html(self,html):
        clean_text = html.lower()
        for re_filter in self.html_rexps:
            clean_text = re_filter.sub(' ',clean_text)
        return clean_text
    def clean_txt(self, text):
        clean_text = text.lower()
        for re_filter in self.txt_rexps:
            clean_text = re_filter.sub(' ',clean_text)
        return clean_text

    def clean(self, html):
        clean_text = self.clean_html()
        return self.clean_txt(clean_text)

