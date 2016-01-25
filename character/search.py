# -*- coding: UTF-8 -*-
'''
search attribute : attention, follower, mention, location, activity
'''
import sys
import csv
import time
import json
import redis
from global_utils import es_user_profile,es_text_profile,MAX_SIZE

#根据uid查询用户属性
def search_profile(uid_list):
    '''
    输入：uid列表
    '''
    es_profile_results = es_user_profile.mget(index='user_portrait_1222', doc_type='user', body={'ids':uid_list})['docs']

    result_list = dict()
    for i in range(len(es_profile_results)):
        item = es_profile_results[i]
        uid = item['_id'].encode('utf-8')
        if item['found']:#有数据
            source = item['_source']
            topic = source['topic_string']
        else:
            topic = ''        

        result_list[uid] = topic
       
    return result_list

#根据uid和date查询用户发布的文本
def search_text(uid_list, date):
    '''
    输入：uid列表、时间
    输出：情绪list、文本list
    '''
    nest_body_list = [{'match':{'uid':item}} for item in uid_list]
    query = [{'bool':{'should': nest_body_list}}]
    try:
        portrait_result = es_text_profile.search(index='flow_text_'+date, doc_type='text', body={'query':{'bool':{'must':query}}, 'size':MAX_SIZE})['hits']['hits']
    except:
        portrait_result = []

    se_result = dict()
    text_result = dict()
    for item in portrait_result:
        source = item['_source']
        uid = source['uid'].encode('utf-8')
        text = source['text'].encode('utf-8')
        sentiment = source['sentiment']
        timestamp = source['timestamp']
        if se_result.has_key(uid):
            row = se_result[uid]
            row.append(sentiment)
            se_result[uid] = row
        else:
            row = []
            row.append(sentiment)
            se_result[uid] = row

        if text_result.has_key(uid):
            row = text_result[uid]
            row = row + '_' + text
            text_result[uid] = row
        else:
            row = text
            text_result[uid] = row 
       
    return se_result,text_result

#以下函数仅作测试使用
def search_test(uid_list, date):
    '''
    输入：uid列表、时间
    输出：情绪list、文本list
    '''
    nest_body_list = [{'match':{'uid':item}} for item in uid_list]
    query = [{'bool':{'should': nest_body_list}}]
    try:
        portrait_result = es_text_profile.search(index='flow_text_'+date, doc_type='text', body={'query':{'bool':{'must':query}}, 'size':MAX_SIZE})['hits']['hits']
    except:
        portrait_result = []

    se_result = dict()
    for item in portrait_result:
        source = item['_source']
        uid = source['uid'].encode('utf-8')
        text = source['text'].encode('utf-8')
        sentiment = source['sentiment']
        timestamp = source['timestamp']
        if se_result.has_key(uid):
            row = se_result[uid]
            row.append([sentiment,text])
            se_result[uid] = row
        else:
            row = []
            row.append([sentiment,text])
            se_result[uid] = row
       
    return se_result    
