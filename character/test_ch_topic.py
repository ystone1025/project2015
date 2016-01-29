# -*- coding: UTF-8 -*-

import sys
import csv
import datetime
import time
from search import search_text_sentiment,search_text,search_profile
from global_utils import WORD_DICT,TOPIC_LIST,EVENT_STA,re_cut,EVENT_DICT
from triple_sentiment_classifier import triple_classifier
from test_data import input_data2

def event_classify(uid_list, uid_dict):
    '''
      批判型的划分：根据用户文本进行划分
      输入数据：字典对象 {uid:[text1,text2,...]...}
      输出结果：dict对象
      1表示批判型，0表示未知
    '''

    uid_count = dict()
    for k in uid_list:
        if uid_dict.has_key(k):
            v = uid_dict[k]
        else:
            v = []
        uid = k
        text_str = ''
        for i in v:
            text_str = text_str + '_' + re_cut(i)

        count = 0
        if len(text_str) <= 2:
            uid_count[uid] = 0
        else:            
            for w in WORD_DICT:
                count = count + text_str.count(w)

        if count >= EVENT_STA:
            uid_count[uid] = 1
        else:
            uid_count[uid] = 0

    return uid_count  

def topic_classify(uid_list):
    '''
      批判型的划分：根据用户话题属性进行划分
      输入数据：uid列表（list对象）
      输出结果：dict对象
      1表示批判型，0表示未知
    '''
    topic_result = search_profile(uid_list)

    topic_dict = dict()
    not_uid = []
    for uid in uid_list:
        item = topic_result[uid]
        if item:
            row = item.split('&')
            com_set = set(row) & set(TOPIC_LIST)
        else:
            com_set = []
        if len(com_set) >= 2:
            flag = 1
        else:
            flag = 0
        topic_dict[uid] = flag

        if flag == 0:
            not_uid.append(uid)

    return topic_dict,not_uid

def classify(uid_weibo,uid_list):
    '''
      有情感标签的分类主函数
      输入数据：list对象 [[uid,text,time],[uid,text,time],...]
      输出数据：字典对象 {uid1:str1,uid2:str2,...}
    '''

    uid_text = dict()
    for uid,text,ts in uid_weibo:
        if uid_text.has_key(uid):
            item = uid_text[uid]
            item.append(text)
            uid_text[uid] = item
        else:
            item = []
            item.append(text)
            uid_text[uid] = item

    t_result,not_uid = topic_classify(uid_list)

    e_result = event_classify(not_uid,uid_text)

    com_result = dict()
    for uid in uid_list:
        if t_result[uid] == 0:
            com_result[uid] = EVENT_DICT[e_result[uid]]
        else:
            com_result[uid] = EVENT_DICT[t_result[uid]]

    return com_result

def classify_topic(uid_list,start_date,end_date,flag):
    '''
        分类主函数：
        输入：用户id列表，查询es的开始时间（字符串），查询es的结束时间（字符串），是否需要再计算情绪（int，1表示需要计算，0表示不需要计算）
        输入样例：[uid1,uid2,uid3,...],'2013-09-01','2013-09-07',0
    '''
    start_ts = int(time.mktime(time.strptime(start_date,'%Y-%m-%d')))
    end_ts = int(time.mktime(time.strptime(end_date,'%Y-%m-%d'))) + 24*3600
    dis = 24*3600

    uid_weibo = []
    for ts in range(start_ts,end_ts,dis):
        date_str = time.strftime('%Y-%m-%d',time.localtime(float(ts)))
        uid_weibo = search_text(uid_list,date_str,uid_weibo)
    print uid_weibo
    com_result = classify(uid_weibo,uid_list)
        
    return com_result
    

###以下函数仅供测试使用，目的是学习对应的参数
def get_event(uid_weibo,name):#学习文本有关的参数

    uid_list = []
    uid_dict = dict()
    for item in uid_weibo:
        uid = item[0]
        text = item[1]
        ts = item[2]
        if uid not in uid_list:
            uid_list.append(uid)
        if uid_dict.has_key(uid):
            item = uid_dict[uid]
            item.append(text)
            uid_dict[uid] = item
        else:
            item = []
            item.append(text)
            uid_dict[uid] = item       

    e_result = event_classify(uid_list, uid_dict)

    write_result(e_result,name) 

def write_result(result_dict,name):

    with open('./result0122/%s_data.csv' % name, 'wb') as f:
        writer = csv.writer(f)
        for k,v in result_dict.iteritems():
            writer.writerow((k,v))

def write_e_result(result_dict,name):

    with open('./result0122/%s_data.csv' % name, 'wb') as f:
        writer = csv.writer(f)
        for k,v in result_dict.iteritems():
            for k1,v1 in v.iteritems():
                writer.writerow((k,k1,v1[0],v1[1],v1[2]))   

if __name__ == '__main__':

    uid_list = input_data2('test_0126')
    start = time.time()
    result_dict = classify_topic(uid_list,'2013-09-01','2013-09-07',0)
    end = time.time()
    print 'it takes %s seconds...' % (end-start)
    print result_dict
##    with open('./result0122/test_0129_data.csv', 'wb') as f:
##        writer = csv.writer(f)
##        for k,v in result_dict.iteritems():
##            writer.writerow((k,v))
##    get_event(uid_weibo,'sta_in_event')
##    get_sentiment(uid_weibo,'sta_in_sentiment')
##    uid_weibo = input_data2('notin')
##    get_event(uid_weibo,'notin_event')
##    get_sentiment(uid_weibo,'notin_sentiment')
    






   
