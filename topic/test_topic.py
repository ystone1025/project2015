#-*-coding=utf-8-*-

import os
import time
import csv
import heapq
import random
from decimal import *
from config import name_list,zh_data,cx_dict,single_word_whitelist,\
                 load_black_words,load_scws,re_cut,load_train

#data_str仅供测试用
data_str = ['20130901','20130902','20130903','20130904','20130905','20130906',\
            '20130907','20130908','20130909','20130910','20130911','20130912',\
            '20130913','20130914','20130915','20130916','20130917','20130918',\
            '20130919','20130920','20130921','20130922','20130923','20130924',\
            '20130925','20130926','20130927','20130928','20130929','20130930']

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

def start_p(data_time):

    domain_p = dict()
    for name in data_time:
        domain_p[name] = 0

    return domain_p

def adjust_dict(word_list,domain_dict):#统计不在语料字典里面的词语数量

    count = 0
    for i in range(0,len(word_list)):
        if domain_dict.has_key(word_list[i]):
            continue
        else:
            count = count + 1

    return count

def com_p(word_list,domain_dict,domain_count,len_dict,total):

    p = 0
    for k,v in word_list.items():
        if domain_dict.has_key(k):
            p1 = float(domain_dict[k]*v)/float(domain_count)
            p = p + p1
        else:
            pass

    return p

def load_weibo(uid_weibo):

    ts = time.time()
    domain_dict,domain_count = load_train()
    end = time.time()

    print '%s' % (end-ts)

    len_dict = dict()
    total = 0
    for k,v in domain_dict.items():
        len_dict[k] = len(v)
        total = total + len(v)

    sw = load_scws()
    black = load_black_words()
    result_data = dict()
    ts = time.time()
    for k,v in uid_weibo.items():
        words = sw.participle(v)
        domain_p = start_p(name_list)
        word_list = dict()
        for word in words:
            if (word[1] in cx_dict) and 3 < len(word[0]) < 30 and (word[0] not in black) and (word[0] not in single_word_whitelist) and (word[0] not in word_list):#选择分词结果的名词、动词、形容词，并去掉单个词
                if word_list.has_key(word[0]):
                    word_list[word[0]] = word_list[word[0]] + 1
                else:
                    word_list[word[0]] = 1
        for d_k in domain_p.keys():
            start = time.time()
            domain_p[d_k] = com_p(word_list,domain_dict[d_k],domain_count[d_k],len_dict[d_k],total)#计算文档属于每一个类的概率
            end_time = time.time()
            print '%s' % (end_time-start)
        result_data[k] = domain_p
        end = time.time()
        print '%s takes %s...' % (k,end-ts)
        ts = end

    return result_data

def rank_dict(has_word):

    n = len(has_word)
    keyword = TopkHeap(n)
    count = 0
    for k,v in has_word.items():
        keyword.Push((v,k))
        count = count + v

    keyword_data = keyword.TopK()
    return keyword_data,count    

def rank_result(result_data):
    
    uid_topic = dict()
    for k,v in result_data.items():
        data_v,count = rank_dict(v)
        if count == 0:
            uid_topic[k] = ['life']
        else:
            uid_topic[k] = [data_v[0][1],data_v[1][1],data_v[2][1]]

    return uid_topic

def topic_classfiy(uid_weibo):#话题分类主函数
    '''
    用户话题分类主函数
    输入数据示例：字典
    {uid1:[weibo1,weibo2,weibo3,...]}

    输出数据示例：字典
    用户18个话题的分布：
    {uid1:{'art':0.1,'social':0.2...}...}
    用户关注较多的话题（最多有3个）：
    {uid1:['art','social','media']...}
    '''
    weibo_text = dict()
    for k,v in uid_weibo.items():
        item = ''
        for i in range(0,len(v)):
            text = re_cut(v[i]['text'])
            item = item + '.' + text
        weibo_text[k] = item

    result_data = load_weibo(weibo_text)#话题分类主函数

    uid_topic = rank_result(result_data)
    
    return result_data,uid_topic

def test_data():#测试输入

    uid_weibo = dict()
    for data in data_str:
        reader = csv.reader(file('./weibo_data/weibo_%s_sensitive_uid_list.csv' % data, 'rb'))
        for line in reader:
            mid = line[1].strip('\t\r\n')
            w_text = line[2].strip('\t\r\n')
            if uid_weibo.has_key(str(mid)):
                item = uid_weibo[str(mid)]
                item_dict = {'uid':mid,'text':w_text}
                item.append(item_dict)
                uid_weibo[str(mid)] = item
            else:
                item = []
                item_dict = {'uid':mid,'text':w_text}
                item.append(item_dict)
                uid_weibo[str(mid)] = item
    
    uid_topic = topic_classfiy(uid_weibo)

    return uid_topic


if __name__ == '__main__':
    
    result_data,uid_topic = test_data()
    print result_data
    print uid_topic







        
