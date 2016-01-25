# -*- coding: UTF-8 -*-

import sys
import csv
import datetime
import time
from search import search_profile,search_text
from global_utils import WORD_DICT,TOPIC_LIST,EVENT_STA,SEN_DICT,EVENT_DICT
from test_data import input_data2,input_data

ZERO_STA = 0.1
RATE_STA = 0.5

def write_csv(users,date):

   with open('./result/uid_weibo_%s.csv' % date, 'wb') as f:
        writer = csv.writer(f)
        for k,v in users.items():
            for i in range(0,len(v)):
                writer.writerow((k,v[i][0],v[i][1],v[i][2]))

def get_rate_by_date(uid_list,ts):#根据用户列表和时间返回用户在该时间下的情绪比例

   t = time.strftime('%Y-%m-%d',time.localtime(ts))
   s_list,t_list = search_text(uid_list,t)
   result = dict()
   for k,s in s_list.iteritems():
      if len(s) == 0:
         result[k] = [0,0]
      else:
         p = s.count(1)
         n = s.count(2) + s.count(3) + s.count(4) + s.count(5) + s.count(6)

         r_p = float(p)/float(len(s))
         r_n = float(n)/float(len(s))

         result[k] = [r_p,r_n]

   return result,t_list

def sentiment_classify(uid_list,date):
   '''
      冲动型+稳定型的区分：
      输入数据：
      用户id列表，当前时间
      输出数据：
      用户类型字典，1表示冲动型，0表示稳定型，2表示未知
   '''
   ts0 = time.mktime(time.strptime(date,'%Y-%m-%d'))
   ts1 = ts0 - 24*60*60
   ts2 = ts1 - 24*60*60

   r0,t0_list = get_rate_by_date(uid_list,ts0)
   r1,t1_list = get_rate_by_date(uid_list,ts1)
   r2,t2_list = get_rate_by_date(uid_list,ts2)

   result = dict()
   for k in uid_list:
      
      count = 0
      if r0.has_key(k) and r1.has_key(k) and r2.has_key(k):
         if r2[k][1] == 0:
            if r1[k][1] > ZERO_STA:
               count = count + 1
         else:
            if abs(r1[k][1]-r2[k][1])/float(r2[k][1]) >= RATE_STA:
               count = count + 1

         if r1[k][1] == 0:
            if r0[k][1] > ZERO_STA:
               count = count + 1
         else:
            if abs(r0[k][1]-r1[k][1])/float(r1[k][1]) >= RATE_STA:
               count = count + 1

         if r2[k][0] == 0:
            if r1[k][0] > ZERO_STA:
               count = count + 1
         else:
            if abs(r1[k][0]-r2[k][0])/float(r2[k][0]) >= RATE_STA:
               count = count + 1

         if r1[k][0] == 0:
            if r0[k][0] > ZERO_STA:
               count = count + 1
         else:
            if abs(r0[k][0]-r1[k][0])/float(r1[k][1]) >= RATE_STA:
               count = count + 1
      elif r0.has_key(k) and r1.has_key(k) and  not (r2.has_key(k)):

         if r1[k][1] == 0:
            if r0[k][1] > ZERO_STA:
               count = count + 2
         else:
            if abs(r0[k][1]-r1[k][1])/float(r1[k][1]) >= RATE_STA:
               count = count + 2

         if r1[k][0] == 0:
            if r0[k][0] > ZERO_STA:
               count = count + 2
         else:
            if abs(r0[k][0]-r1[k][0])/float(r1[k][1]) >= RATE_STA:
               count = count + 2
               
      elif r0.has_key(k) and not (r1.has_key(k)) and  r2.has_key(k):

         count = 4
         
      elif not (r0.has_key(k)) and r1.has_key(k) and  r2.has_key(k):

         if r2[k][1] == 0:
            if r1[k][1] > ZERO_STA:
               count = count + 2
         else:
            if abs(r1[k][1]-r2[k][1])/float(r2[k][1]) >= RATE_STA:
               count = count + 2
               
         if r2[k][0] == 0:
            if r1[k][0] > ZERO_STA:
               count = count + 2
         else:
            if abs(r1[k][0]-r2[k][0])/float(r2[k][0]) >= RATE_STA:
               count = count + 2
      elif not (r0.has_key(k)) and not (r1.has_key(k)) and  not (r2.has_key(k)):
         count = -1
      else:
         count = 4
      
      if count == 4:
         result[k] = 1
      elif count == -1:
         result[k] = 2
      else:
         result[k] = 0

   t_list = [t0_list,t1_list,t2_list]
   
   return result,t_list

def event_classify(uid_list,t_list):
   '''
      批判型+中立型的区分：根据用户文本进行划分
      输出结果：dict对象
      1表示批判型，0表示中立型，2表示未知
   '''

   uid_count = dict()
   for uid in uid_list:
      count = 0
      if t_list[0].has_key(uid):
         s0 = t_list[0][uid]
      else:
         s0 = ''
      if t_list[1].has_key(uid):
         s1 = t_list[1][uid]
      else:
         s1 = ''
      if t_list[2].has_key(uid):
         s2 = t_list[2][uid]
      else:
         s2 = ''

      text_s = s0 + '_' + s1 + '_' + s2
      if len(text_s) <= 2:
         uid_count[uid] = 2
      else:
         for w in WORD_DICT:
            count = count + text_s.count(w)

         if count >= EVENT_STA:
            uid_count[uid] = 1
         else:
            uid_count[uid] = 0

   return uid_count   

def topic_classify(uid_list):
   '''
      批判型+中立型的区分：根据用户话题属性进行划分
      输出结果：dict对象
      1表示批判型，0表示中立型，2表示未知
   '''
   topic_result = search_profile(uid_list)

   topic_dict = dict()
   not_uid = []
   for uid in uid_list:
      item = topic_result[uid]
      if item:
         row = item.split('&')
         com_set = set(row) & set(TOPIC_LIST)
         if len(com_set) >= 2:
            flag = 1
         else:
            flag = 0
      else:
         flag = 0
      topic_dict[uid] = flag
      if flag == 0:
         not_uid.append(uid)

   return topic_dict,not_uid   

def classify_main(uid_list,date):
   '''
      分类主函数
   '''
    
   s_result,t_list = sentiment_classify(uid_list,date)

   t_result,not_uid = topic_classify(uid_list)

   e_result = event_classify(not_uid,t_list)

   com_result = dict()
   for uid in uid_list:
      if t_result[uid] == 0:
         com_result[uid] = [SEN_DICT[s_result[uid]],EVENT_DICT[e_result[uid]]]
      else:
         com_result[uid] = [SEN_DICT[s_result[uid]],EVENT_DICT[t_result[uid]]]

   return com_result

def test(uid_list,date,name):

   s_result,t_list = sentiment_classify(uid_list,date)

   e_result = event_classify(uid_list,t_list)

   with open('./result0122/%s_data_%s.csv' % (name,date), 'wb') as f:
        writer = csv.writer(f)
        for uid in uid_list:
           writer.writerow((uid,s_result[uid],e_result[uid]))

def write_result(result_dict,date,name):

   with open('./result0122/%s_data_%s.csv' % (name,date), 'wb') as f:
        writer = csv.writer(f)
        for k,v in result_dict.iteritems():
           writer.writerow((k,v[0],v[1]))
   

if __name__ == '__main__':

   uid_list = input_data2('0122')
   print len(uid_list)
   for i in range(3,8):
      start = time.time()
      date = '2013-09-0' + str(i)
      com_result = classify_main(uid_list,date)
      write_result(com_result,date,'unkown')
      end = time.time()
      print '%s takes %s seconds...' % (date,(end-start))

##   uid_list = input_data2('test')
##   for i in range(3,8):
##      date = '2013-09-0' + str(i)
##      test(uid_list,date,'test')






   
