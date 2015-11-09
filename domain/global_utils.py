# -*- coding: utf-8 -*-

import os
import re
import scws
import redis
from elasticsearch import Elasticsearch
from xapian_weibo.xapian_backend import XapianSearch

REDIS_HOST = '219.224.135.97'
REDIS_PORT = '6380'

def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=1):
    return redis.StrictRedis(host, port, db)

R_0 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
R_1 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=1)
R_2 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=2)
R_3 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=3)
R_4 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=4)
R_5 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
R_6 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=6)
R_7 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=7)
R_8 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=8)
R_9 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=9)
R_10 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=10)
R_11 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=11)
R_12 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=12)
R_13 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=13)
R_14 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=14)

R_DICT = {'0':R_0, '1':R_1, '2':R_2, '3':R_3, '4':R_4, '5':R_5, '6':R_6, '7':R_7,\
          '8':R_8, '9':R_9, '10':R_10, '11':R_11, '12':R_12, '13':R_13,\
          '14':R_14}

USER_PORTRAIT_ES_HOST = ['219.224.135.93:9200', '219.224.135.94:9200']
USER_PROFILE_ES_HOST = ['219.224.135.96:9208','219.224.135.97:9208','219.224.135.98:9208']
es_user_profile = Elasticsearch(USER_PROFILE_ES_HOST, timeout = 60)
es_user_portrait = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)

##加载领域标签

labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'other', 'business']
zh_labels = ['高校', '境内机构', '境外机构', '媒体', '境外媒体', '民间组织', '法律机构及人士', \
             '政府机构及人士', '媒体人士', '活跃人士', '草根', '其他', '商业人士']
txt_labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'business']
r_labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg',]
outlist = ['海外', '香港', '台湾', '澳门']
lawyerw = ['律师', '法律', '法务', '辩护']
STATUS_THRE = 4000
FOLLOWER_THRE = 1000

##领域标签加载结束

##对微博文本进行预处理

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
    if w_text == '转发微博':
        w_text = ''

    return w_text

##微博文本预处理结束

## 加载分词工具

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './dict'))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')

cx_dict = ['an','Ng','n','nr','ns','nt','nz','vn','@']#关键词词性词典

def load_one_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_EMOTIONWORD_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())

def load_scws():
    s = scws.Scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s

def cut(s, text, f=None, cx=False):
    if f:
        tks = [token for token
               in s.participle(cut_filter(text))
               if token[1] in f and (3 < len(token[0]) < 30 or token[0] in single_word_whitelist)]
    else:
        tks = [token for token
               in s.participle(cut_filter(text))
               if 3 < len(token[0]) < 30 or token[0] in single_word_whitelist]
    if cx:
        return tks
    else:
        return [tk[0] for tk in tks]
##加载分词工具结束

##加载xapian读取用户的认证类型
XAPIAN_USER_DATA_PATH = '/home/xapian/xapian_user/'
xs = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)

def read_by_xapian(xs,uid):#根据用户id，去xapian里面查找该用户的背景信息

    count,get_results = xs.search(query={'_id': uid})
    if count:
        for r in get_results():
            return r
    else:
        return 'other'
##加载xapian数据结束
