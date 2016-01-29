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

#根据uid和date查询用户发布的文本，此接口表示每条微博的情绪已经计算完成
def search_text_sentiment(uid_list, date, result):
    '''
    输入：uid列表、时间
    输出：情绪list、文本list
    '''
    nest_body_list = [{'match':{'uid':k}} for k in uid_list]
    query = [{'bool':{'should': nest_body_list}}]
    try:
        portrait_result = es_text_profile.search(index='flow_text_'+date, doc_type='text', body={'query':{'bool':{'must':query}}, 'size':MAX_SIZE})['hits']['hits']
    except:
        portrait_result = []

    for item in portrait_result:
        source = item['_source']
        uid = source['uid'].encode('utf-8')
        text = source['text'].encode('utf-8')
        sentiment = source['sentiment']
        timestamp = source['timestamp']
        result.append([uid,text,sentiment,timestamp])
       
    return result  

#根据uid和date查询用户发布的文本，此接口表示没有计算每条微博的情绪或者情绪计算不准确
def search_text(uid_list, date, result):
    '''
    输入：uid列表、时间
    输出：情绪list、文本list
    '''
    nest_body_list = [{'match':{'uid':k}} for k in uid_list]
    query = [{'bool':{'should': nest_body_list}}]
    try:
        portrait_result = es_text_profile.search(index='flow_text_'+date, doc_type='text', body={'query':{'bool':{'must':query}}, 'size':MAX_SIZE})['hits']['hits']
    except:
        portrait_result = []

    for item in portrait_result:
        source = item['_source']
        uid = source['uid'].encode('utf-8')
        text = source['text'].encode('utf-8')
        timestamp = source['timestamp']
        result.append([uid,text,timestamp])
       
    return result 
