#-*-coding=utf-8-*-

import os
import time
import csv
import scws
import re
import heapq
from config import load_scws,re_cut,load_dict,s_label,f_label

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

def find_label(text,sw,df_dict,df_count,ds_dict,ds_count):

    words = sw.participle(text)
    s_data = ['anger','anx','sad']#第二层分类标签
    f_data = ['negemo','posemo']#第一层分类标签
    domain_f = start_p(f_data)
    domain_s = start_p(s_data)
    for word in words:
        for d_k,d_v in df_dict.items():
            if str(word[0]) in d_v:
                domain_f[d_k] = domain_f[d_k] + 1
        for d_k,d_v in ds_dict.items():
            if str(word[0]) in d_v:
                domain_s[d_k] = domain_s[d_k] + 1

    max_f = 0
    label_f = 'middle'
    for k1,v1 in domain_f.items():
        domain_f[k1] = float(v1)/float(df_count[k1])
        if domain_f[k1] > max_f:
            max_f = domain_f[k1]
            label_f = k1

    max_s = 0
    label_s = 'other'
    for k1,v1 in domain_s.items():
        domain_s[k1] = float(v1)/float(ds_count[k1])
        if domain_s[k1] > max_s:
            max_s = domain_s[k1]
            label_s = k1

    return label_f,label_s

def psychology_classfiy(uid_weibo):#心理状态分类主函数
    '''
    用户心理状态分类主函数
    输入数据示例：字典
    {uid1:[weibo1,weibo2,weibo3,...]}

    输出数据示例：字典(每个用户对应两个字典，一个是一层分类器的状态比例，另一个是二层分类器（消极状态）的状态比例)
    {uid1:{'first':{'negemo':0.2,'posemo':0.3,'middle':0.5},'second':{'anger':0.2,'anx':0.5,'sad':0.1,'other':0.2}}...}
    '''
    
    df_dict,df_count = load_dict(f_label)
    ds_dict,ds_count = load_dict(s_label)
    
    data_s = s_label
    data_f = f_label
    data_s.append('other')
    data_f.append('middle')

    sw = load_scws()
    result_data = dict()
    for k,v in uid_weibo.items():
        domain_f = start_p(data_f)
        domain_s = start_p(data_s)
        for i in range(0,len(v)):
            w_text = re_cut(v[i])
            if not len(w_text):
                continue
            label_f,label_s = find_label(w_text,sw,df_dict,df_count,ds_dict,ds_count)
            domain_f[label_f] = domain_f[label_f] + 1
            domain_s[label_s] = domain_s[label_s] + 1

        for k1,v1 in domain_f.items():
            domain_f[k1] = float(v1)/float(len(v))
        for k1,v1 in domain_s.items():
            if domain_f['negemo'] != 0:
                domain_s[k1] = float(v1)/float(len(v))
            else:
                domain_s[k1] = 0

        result_data[k] = {'first' : domain_f, 'second' : domain_s}

    return result_data

def test_input(name):#测试用输入

    uid_weibo = dict()
    reader = csv.reader(file('./weibo_data/weibo_%s.csv'% name, 'rb'))
    for mid,w_text in reader:
        if uid_weibo.has_key(str(mid)):
            item = uid_weibo[str(mid)]
            item.append(w_text)
            uid_weibo[str(mid)] = item
        else:
            item = []
            item.append(w_text)
            uid_weibo[str(mid)] = item

    return uid_weibo

def write_file(result_data,name):
    
    with open('./result/result_%s.csv' % name, 'wb') as f:
        writer = csv.writer(f)
        for k,v in result_data.items():
            row = []
            row.append(k)
            first = v['first']
            second = v['second']
            for k1,v1 in first.items():
                w = str(v1) + '*' + str(k1)
                row.append(w)
            for k1,v1 in second.items():
                w = str(v1) + '*' + str(k1)
                row.append(w)
            writer.writerow((row))

if __name__ == '__main__':

    uid_weibo = test_input('0716')
    result_data = psychology_classfiy(uid_weibo)
    write_file(result_data,'0716')
