#-*-coding=utf-8-*-
#vision2
import os
import re
import sys
import json
import csv
import time
import datetime

def input_data():#测试输入

    uid_weibo = []
    reader = csv.reader(file('./test_weibo/com_weibo0126.csv', 'rb'))
    for mid,w_text,ts in reader:
        mid = mid.strip('\xef\xbb\xbf')
        uid_weibo.append(mid)
    
    return uid_weibo

def input_data2(name):#测试输入
    
    uid_list = []
    reader = csv.reader(file('./weibo_data/%s_uid.txt' % name, 'rb'))
    for line in reader:
        uid = line[0].strip('\t\r\n')
        uid = uid.strip('\xef\xbb\xbf')
        uid_list.append(uid)

    uid_weibo = []
    reader = csv.reader(file('./test_weibo/com_weibo0126.csv', 'rb'))
    for mid,w_text,ts in reader:
        mid = mid.strip('\xef\xbb\xbf')
        if mid in uid_list:
            uid_weibo.append(mid)
    
    return uid_weibo


def combine_weibo():

    name_list = ['2013-09-01','2013-09-02','2013-09-03','2013-09-04',\
                 '2013-09-05','2013-09-06','2013-09-07']

    weibo_list = []
    for name in name_list:
        reader = csv.reader(file('./test_weibo/word_%s.csv' % name, 'rb'))
        ts = int(time.mktime(time.strptime(name,'%Y-%m-%d')))
        for mid,s,w_text in reader:
            mid = mid.strip('\xef\xbb\xbf')
            weibo_list.append([mid,w_text,ts])

    with open('./test_weibo/com_weibo0126.csv', 'wb') as f:
        writer = csv.writer(f)
        for item in weibo_list:
           writer.writerow((item[0],item[1],item[2]))

if __name__ == '__main__':
    combine_weibo()
            
    
