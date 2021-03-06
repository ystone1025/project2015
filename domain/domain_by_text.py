#-*-coding=utf-8-*-

import os
import re
import sys
import json
import csv
import heapq
import scws
import time
from decimal import *
from global_utils import txt_labels,load_scws,load_black_words,single_word_whitelist,cx_dict

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

def start_p():

    domain_p = dict()
    for name in txt_labels:
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
    #count = adjust_dict(word_list,domain_dict)
    for k,v in word_list.items():
        if domain_dict.has_key(k):
            p1 = float(domain_dict[k]*v)/float(domain_count)
            p = p + p1
        else:
            pass

    return p

def load_train():

    domain_dict = dict()
    domain_count = dict()
    for i in txt_labels:
        reader = csv.reader(file('./topic_dict/%s.csv'% i, 'rb'))
        word_dict = dict()
        count = 0
        for f,w_text in reader:
            f = f.strip('\xef\xbb\xbf')
            word_dict[str(w_text)] = float(f)
            count = count + float(f)
        domain_dict[i] = word_dict
        domain_count[i] = count

    return domain_dict,domain_count

def rank_dict(has_word):

    n = len(has_word)
    keyword = TopkHeap(n)
    count = Decimal(0)
    for k,v in has_word.items():
        keyword.Push((v,k))
        count = count + Decimal(v)

    if count > 0:
        keyword_data = keyword.TopK()
        label = txt_labels[txt_labels.index(keyword_data[0][1])]
    else:
        label = 'other'
        keyword_data = keyword.TopK()
    return label,keyword_data

def domain_classfiy_by_text(user_weibo):#根据用户微博文本进行领域分类
    '''
    输入数据：字典
    {uid:weibo字符串(多条微博用逗号连接),...}
    输出数据：字典
    {uid:label1,uid2:label2,...}
    '''
    domain_dict,domain_count = load_train()
    len_dict = dict()
    total = 0
    for k,v in domain_dict.items():
        len_dict[k] = len(v)
        total = total + len(v)

    sw = load_scws()
    black = load_black_words()
    result_data = dict()
    p_data = dict()
    for k,v in user_weibo.items():
        start = time.time()
        words = sw.participle(v)
        domain_p = start_p()
        word_list = dict()
        for word in words:
            if (word[1] in cx_dict) and 3 < len(word[0]) < 30 and (word[0] not in black) and (word[0] not in single_word_whitelist):#选择分词结果的名词、动词、形容词，并去掉单个词
                if word_list.has_key(word[0]):
                    word_list[word[0]] = word_list[word[0]] + 1
                else:
                    word_list[word[0]] = 1
        for d_k in domain_p.keys():
            start_time = time.time()
            domain_p[d_k] = com_p(word_list,domain_dict[d_k],domain_count[d_k],len_dict[d_k],total)#计算文档属于每一个类的概率
            end_time = time.time()
            print '%s domain takes %s second...' % (d_k,(end_time-start_time))
        label,rank_data = rank_dict(domain_p)
        result_data[k] = label
        p_data[k] = rank_data
        end = time.time()
        print '%s takes %s second...' % (k,(end-start))

    return result_data,p_data

def test_data():#测试输入

    uid_weibo = dict()
    reader = csv.reader(file('./weibo_data/uid_text_0727.csv', 'rb'))
    for mid,w_text in reader:
        if uid_weibo.has_key(str(mid)):
            item = uid_weibo[str(mid)]
            item = item + ',' + w_text
            uid_weibo[str(mid)] = item
        else:
            item = w_text
            uid_weibo[str(mid)] = item

    result_data = domain_classfiy_by_text(uid_weibo)

    for k,v in result_data.items():
        print k,v

if __name__ == '__main__':

    test_data()
    
