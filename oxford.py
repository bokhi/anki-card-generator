import codecs
import urllib2 
from HTMLParser import HTMLParser
import re
import sys

from StringIO import StringIO
import gzip


class Article:
    def __init__(self):
        self.pageTitle = ''
        self.syllabification = ''
        self.headpron = []
        self.variant = ''
        self.senseGroup = []

class SenseGroup:
    def __init__(self):
        self.partOfSpeech = ''
        self.pronunciation = []
        self.sense = []

class Sense:
    def __init__(self):
        self.definition = ''
        self.example = []

class OxfordHTML(HTMLParser):
    '''A simple parser for oxford dictionary webpages'''

    def __init__(self):
        HTMLParser.__init__(self)
        self.article = Article()
        self.level_senseGroup = -1
        self.flag_senseGroup = False
        self.level_sense = -1
        self.flag_article = False
        self.flag_pageTitle = False
        self.flag_syllabification = False
        self.flag_headpron = False
        self.flag_variant = False
        self.flag_senseInnerWrapper = False
        self.flag_partOfSpeech = False
        self.flag_pronunciation = False
        self.flag_definition = False
        self.flag_example = False
        self.flag_found = False
        self.flag_etym = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.flag_article = True
            self.flag_found = True
        elif self.flag_article:
            for name, value in attrs:
                if tag == 'span':
                    if name == 'class' and value == 'pageTitle':
                        self.flag_pageTitle = True
                    elif name == 'class' and value == 'syllabification':
                        self.flag_syllabification = True
                    elif name == 'class' and value == 'headpron':
                        self.flag_headpron = True
                    elif name == 'class' and value == 'variant':
                        self.flag_variant = True
                    elif name == 'class' and value == 'partOfSpeech' and self.flag_senseGroup:
                        self.flag_partOfSpeech = True
                    elif name == 'class' and value == 'pronunciation' and self.flag_senseGroup:
                        self.flag_pronunciation = True
                    elif name == 'class' and value == 'definition' and self.flag_senseGroup:
                        self.flag_definition = True
                elif tag == 'em':
                    if name == 'class' and value == 'example' and self.flag_senseGroup:
                        self.flag_example = True
                        self.article.senseGroup[self.level_senseGroup].sense[self.level_sense].example.append('')
                elif tag == 'div':
                    if name == 'class' and value == 'senseGroup':
                        self.level_senseGroup += 1
                        self.flag_senseGroup = True
                        self.article.senseGroup.append(SenseGroup())
                    elif name == 'class' and value == 'senseInnerWrapper':
                        self.level_sense += 1
                        self.flag_senseInnerWrapper = True
                        self.article.senseGroup[self.level_senseGroup].sense.append(Sense())
                    elif name == 'class' and value == 'sense-etym':
                        self.flag_etym = True
                    
    def handle_endtag(self, tag):
        if tag == 'article':
            self.flag_article = False
        if self.flag_article:
            if tag == 'span':
                if self.flag_pageTitle:
                    self.flag_pageTitle = False
                elif self.flag_syllabification:
                    self.flag_syllabification = False
                elif self.flag_headpron:
                    self.flag_headpron = False
                    self.article.headpron = self.article.headpron[1]
                elif self.flag_partOfSpeech:
                    self.flag_partOfSpeech = False
                elif self.flag_variant:
                    self.flag_variant = False
                elif self.flag_pronunciation:
                    self.flag_pronunciation = False
                    self.article.senseGroup[self.level_senseGroup].pronunciation = self.article.senseGroup[self.level_senseGroup].pronunciation[1]
                elif self.flag_definition:
                    self.flag_definition = False
            elif tag == 'em':
                if self.flag_example:
                    self.flag_example = False
            elif tag == 'div':
                if self.flag_etym:
                    self.flag_etym = False
                elif self.flag_senseInnerWrapper:
                    self.flag_senseInnerWrapper = False
                elif self.flag_senseGroup:
                    self.level_sense = -1
                    self.flag_senseGroup = False
                
    def handle_data(self, data):
        if self.flag_article:
            if self.flag_pageTitle:
                self.article.pageTitle = data
            elif self.flag_syllabification:
                self.article.syllabification = data
            elif self.flag_headpron:
                self.article.headpron.append(data)
            elif self.flag_variant:
                self.article.variant = data
            elif self.flag_partOfSpeech:
                self.article.senseGroup[self.level_senseGroup].partOfSpeech = data
            elif self.flag_pronunciation:
                self.article.senseGroup[self.level_senseGroup].pronunciation.append(data)
            elif self.flag_definition:
                insensitive_word = re.compile(re.escape(self.article.pageTitle), re.IGNORECASE)
                self.article.senseGroup[self.level_senseGroup].sense[self.level_sense].definition += insensitive_word.sub('~', data)
            elif self.flag_example:
                self.article.senseGroup[self.level_senseGroup].sense[self.level_sense].example[-1] += data

def generate(words):
    file = codecs.open("oxford.txt", "w", "utf-8")
    
    for word in words:
        
        url = "http://oxforddictionaries.com/search/english/?direct=1&multi=1&q=" + word.replace(' ', '+')
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.11 (KHTML, like Gecko) Ubuntu/12.04 Chromium/20.0.1132.47 Chrome/20.0.1132.47 Safari/536.11'}
        
        req = urllib2.Request(url,None,headers)

        page_source = urllib2.urlopen(req,None)

        charset = page_source.headers.getparam('charset')

        oxford = OxfordHTML()        

        if page_source.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( page_source.read())
            f = gzip.GzipFile(fileobj=buf)
            oxford.feed(f.read().decode(charset))
        else:
            oxford.feed(page_source.read().decode(charset))

        if not oxford.flag_found:
            print word, 'page not found'

        else:
            print word
            for senseg in oxford.article.senseGroup:
                for sense in senseg.sense:
                    if sense.definition != '':
                        file.write(sense.definition + '<br><br>')

            file.write('\t')
            if oxford.article.headpron != []:
                file.write(oxford.article.pageTitle + ': ' + oxford.article.headpron + ' ' + oxford.article.syllabification + ' ' + oxford.article.variant + '<br>')
            for senseg in oxford.article.senseGroup:
                if senseg.partOfSpeech != '':
                    file.write(senseg.partOfSpeech)
                if senseg.pronunciation != []:
                    file.write(senseg.pronunciation + '<br>')
                elif senseg.partOfSpeech != '':
                    file.write('<br>')
                for sense in senseg.sense:
                    if sense.definition != '':
                        file.write(sense.definition + '<br>')                        
                        for example in sense.example:
                            if example != []:
                                file.write(example + '<br>')
                        file.write('<br>')
            file.write('\n')
            del oxford
    file.close()

if __name__ == "__main__":
    words = open(str(sys.argv[1])).read().splitlines()
    generate(words)
