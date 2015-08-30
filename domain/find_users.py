# -*- coding: UTF-8 -*-

import os
import time
import scws
import csv
import sys
import json
from search import search_follower
from search_user_profile import es_get_source

zh_text = ['nick_name','rel_name','description','sp_type','user_location']

def find_friends(uids):

    friends_list = dict()
    for uid in uids:
        v = search_follower(uid)
        item = []
        if not v:
            friends_list[str(uid)] = []
            continue
        for i in v.keys():
            item.append(i)
        friends_list[str(uid)] = item

    return friends_list

def get_info(uids):

    friends_list = dict()
    for uid in uids:
        #print uid
        data = es_get_source(uid)
        item = dict()
        if not data:
            friends_list[str(uid)] = 'other'
            continue
        for k,v in data.items():
            if k in set(zh_text):
                item[k] = v.encode('utf-8')
            else:
                item[k] = v
        friends_list[str(uid)] = item

    return friends_list

def write_user(friends,area):

    fw = open('./dogapi_combine/'+area+'_info.jl','w')
    for k,v in friends.items():
        data = {'user':v,'id':k}
        d = json.dumps(data)
        fw.write(d + '\n')

def write_friends(friends,area):

    fw = open('./dogapi_combine/'+area+'_friends.jl','w')
    for k,v in friends.items():
        data = {'friends':v,'id':k}
        d = json.dumps(data)
        fw.write(d + '\n')

def readUidByArea(area):
    uidlist = []
    with open("./domain_combine/" + area +".txt") as f:
        for line in f:
            uid = line.split()[0]
            uid = uid.strip('\ufeff')
            uidlist.append(uid)
    return uidlist

def readcsv(name):

    f = open('./test_user/uid_%s.txt' % name)
    uidlist = []
    for line in f:
        line = line.strip('\r\n')
        uidlist.append(line)

    return uidlist

def train_data():#训练数据
    classes = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'business']

    for area in classes:
        print '%s start....' % area
        uidlist = readUidByArea(area)
        friend_list = find_friends(uidlist)
        user_info = get_info(uidlist)
        write_friends(friend_list,area)
        write_user(user_info,area)
        print '%s end....' % area

def get_user(uidlist):#返回用户的背景信息
    '''
        返回用户的景信息
        输入数据：uid列表
        输出数据：users列表
    '''

    user_info = get_info(uidlist)        

    return user_info

def get_friends(uidlist):#返回用户的粉丝结构
    '''
        返回用户的粉丝结构
        输入数据：uid列表
        输出数据：friend列表
    '''

    friend_list = find_friends(uidlist)
    
    return friend_list

if __name__ == '__main__':

    train_data()

    
    
