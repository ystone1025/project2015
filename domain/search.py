# -*- coding: UTF-8 -*-
'''
search attribute : attention, follower, mention, location, activity
'''
#import IP
import sys
import csv
import time
import json
import redis
from global_utils import R_DICT

#search:'be_retweet_' + str(uid) return followers {br_uid1:count1, br_uid2:count2}
#redis:{'be_retweet_'+uid:{br_uid:count}}
#return results:{br_uid:[uname, count]}
def search_follower(uid):
    results = dict()
    stat_results = dict()
    for db_num in R_DICT:
        r = R_DICT[db_num]
        br_uid_results = r.hgetall('be_retweet_'+str(uid))
        #print 'br_uid_results:', br_uid_results
        if br_uid_results:
            for br_uid in br_uid_results:
                try:
                    stat_results[br_uid] += br_uid_results[br_uid]
                except:
                    stat_results[br_uid] = br_uid_results[br_uid]
    # print 'stat_results:', stat_results
    for br_uid in stat_results:
        # search uid
        '''
        uname = search_uid2uname(br_uid)
        if not uname:
        '''
        uname = '未知'
        
        count = stat_results[br_uid]
        results[br_uid] = [uname, count]
    if results:
        return results
    else:
        return None


    
