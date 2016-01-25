# -*- coding: utf-8 -*-

import re
import csv
from elasticsearch import Elasticsearch

#查询人物属性的es配置
USER_PROFILE_ES_HOST = ['219.224.135.91:9200','219.224.135.92:9200','219.224.135.93:9200']
es_user_profile = Elasticsearch(USER_PROFILE_ES_HOST, timeout = 60)

#查询文本的es配置
TEXT_ES_HOST = ['219.224.135.91:9206','219.224.135.92:9206','219.224.135.93:9206']
es_text_profile = Elasticsearch(TEXT_ES_HOST, timeout = 60)

def load_words():

    reader = csv.reader(file('./topic_dict/train_words.csv', 'rb'))
    word_dict = []
    count = 0
    for line in reader:
        f = line[0]
        f = f.strip('\xef\xbb\xbf')
        if f not in word_dict:
            word_dict.append(f)

    return word_dict

WORD_DICT = load_words()

TOPIC_LIST = ['politics','anti-corruption','fear-of-violence','peace','religion']
EVENT_STA = 700
MAX_SIZE = 9999999

SEN_DICT = {1:'冲动',0:'稳定',2:'未知'}
EVENT_DICT = {1:'批判',0:'中立',2:'未知'}

def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text

def re_cut(w_text):#根据一些规则把无关内容过滤掉
    
    w_text = cut_filter(w_text)
    w_text = re.sub(r'[a-zA-z]','',w_text)
    a1 = re.compile(r'\[.*?\]' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s' )
    w_text = a1.sub('',w_text)
    if w_text == u'转发微博':
        w_text = ''

    return w_text
