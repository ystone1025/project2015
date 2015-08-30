#-*-coding=utf-8-*-

import os
import time
import scws
import csv
import heapq
import codecs
from decimal import *
from config import name_list,cx_dict,single_word_whitelist,\
                 load_black_words,load_scws,re_cut,load_train_ori

def read_csv(domain_dict,domain_count,d_time):
    sw = load_scws()
    black = load_black_words()
    text = ''
    word_dict = dict()
    reader = csv.reader(file('./add_dict/%s_new.csv'% d_time, 'rb'))
    for line in reader:
        #line = line[0].strip('\xef\xbb\xbf')
        #line = line.strip('\n')
        text = text + ',' + line

    #print text.encode('utf-8')
    words = sw.participle(text)
    for word in words:
        if (word[1] in cx_dict) and (3 < len(word[0]) < 30 or word[0] in single_word_whitelist) and (word[0] not in black):#选择分词结果的名词、动词、形容词，并去掉单个词
            if domain_dict.has_key(str(word[0])):
                domain_dict[str(word[0])] = domain_dict[str(word[0])] + 1
            else:
                domain_dict[str(word[0])] = 1
            domain_count = domain_count + 1

    return domain_dict,domain_count

def write_has(filename,has_word):

    n = len(has_word)
    keyword = TopkHeap(n)

    for k,v in has_word.items():
        keyword.Push((v,k))

    keyword_data = keyword.TopK()

    with open('./topic_dict/%s_ori.csv' % filename, 'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(keyword_data)):
            if keyword_data[i][0] > 1:
                writer.writerow((keyword_data[i][0],keyword_data[i][1]))

if __name__ == '__main__':

    domain_dict,domain_count = load_train_ori()
    
    for j in name_list:
        print '%s start...' % j
        new_dict,new_count = read_csv(domain_dict[j],domain_count[j],j)#更新类型字典
        print '%s end...' % j
        write_has(j,new_dict)#将结果写入文件
    
