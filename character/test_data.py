#-*-coding=utf-8-*-
#vision2
import os
import re
import sys
import json
import csv

def input_data():#测试输入

    uid_weibo = []
    reader = csv.reader(file('./weibo_data/uid_text_0728.csv', 'rb'))
    for mid,w_text in reader:
        if mid not in uid_weibo:
            uid_weibo.append(mid)
    
    return uid_weibo

def input_data2(name):#测试输入

    uid_weibo = []
    reader = csv.reader(file('./weibo_data/%s_uid.txt' % name, 'rb'))
    for line in reader:
        uid = line[0].strip('\t\r\n')
        uid = uid.strip('\xef\xbb\xbf')
        uid_weibo.append(uid)
    
    return uid_weibo

