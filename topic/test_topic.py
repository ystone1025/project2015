#-*-coding=utf-8-*-

import os
import time
import csv
import heapq
import random
from decimal import *
from config import name_list,zh_data,cx_dict,single_word_whitelist,\
                 load_black_words,load_scws,re_cut,load_train

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

    p = Decimal(1.0)
    getcontext().prec = 50
    count = adjust_dict(word_list,domain_dict)
    for i in range(0,len(word_list)):
        if domain_dict.has_key(word_list[i]):
            p1 = Decimal((domain_dict[word_list[i]]+count)*len_dict)/Decimal((domain_count+len(domain_dict)*count)*total)
            p = p * p1
        else:
            p1 = Decimal(1*len_dict)/Decimal((domain_count+len(domain_dict)*count)*total)
            p = p * p1

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
        word_list = []
        for word in words:
            if (word[1] in cx_dict) and 3 < len(word[0]) < 30 and (word[0] not in black) and (word[0] not in single_word_whitelist) and (word[0] not in word_list):#选择分词结果的名词、动词、形容词，并去掉单个词
                word_list.append(word[0])
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
    for k,v in has_word.items():
        keyword.Push((v,k))

    keyword_data = keyword.TopK()
    return keyword_data    

def rank_result(result_data):
    
    uid_topic = dict()
    for k,v in result_data.items():
        data_v = rank_dict(v)
        item = dict()
        for i in range(0,len(data_v)):
            item[zh_data[name_list.index(data_v[i][1])]] = data_v[i][0]
        uid_topic[k] = item

    return uid_topic

def topic_classfiy(uid_weibo):#话题分类主函数
    '''
    用户话题分类主函数
    输入数据示例：字典
    {uid1:[weibo1,weibo2,weibo3,...]}

    输出数据示例：字典
    {uid1:{'art':0.1,'social':0.2...}...}
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
    
    return uid_topic

def test_data():#测试输入

    uid_weibo = dict()
    reader = csv.reader(file('./weibo_data/uid_text_0728.csv', 'rb'))
    for mid,w_text in reader:
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

##    rand_weibo = dict()
##    for k,v in uid_weibo.items():#从所有已标注样本中随机抽取数据进行测试
##        f = random.randint(1, 8)
##        if f == 4:
##            rand_weibo[k] = v
    
    uid_topic = topic_classfiy(uid_weibo)

    return uid_topic

def write_topic(uid_topic):

    with open('./result/result_topic0802.csv', 'wb') as f:
        writer = csv.writer(f)
        for k,v in uid_topic.items():
            row = []
            row.append(k)
            data_v = rank_dict(v)
            writer.writerow((k,data_v[0][1]))

if __name__ == '__main__':
    
    uid_topic = test_data()
    write_topic(uid_topic)







        
