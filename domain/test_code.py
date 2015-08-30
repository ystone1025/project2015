#-*-coding=utf-8-*-

import os
import csv

labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'other', 'business']
zh_labels = ['高校', '境内机构', '境外机构', '媒体', '境外媒体', '民间组织', '法律机构及人士', \
             '政府机构及人士', '媒体人士', '活跃人士', '其他组织', '其他', '商业人士']

def load_label():

    user_label = dict()
    reader = csv.reader(file('./result/test3000.csv', 'rb'))
    for uid,text in reader:
        uid = uid.strip('\t\r\n')
        text = text.strip('\t\r\n')
        label = labels[zh_labels.index(text)]
        user_label[uid] = label

    return user_label

def test_data():

    uid_weibo = []
    reader = csv.reader(file('./uid_text_0728.csv', 'rb'))
    for mid,w_text in reader:
        mid  = mid.strip('\t\r\n')
        if mid not in uid_weibo:
            uid_weibo.append(mid)

    return uid_weibo

def load_data(name):

    user_test = dict()
    reader = csv.reader(file('./result/result%s.csv' % name, 'rb'))
    for uid,text in reader:
        uid = uid.strip('\t\r\n')
        text = text.strip('\t\r\n')
        label = labels[zh_labels.index(text)]
        user_test[uid] = label

    return user_test

def main(name):
    user_label = load_label()
    #uid_list = test_data()
    user_test = load_data(name)

    count = 0
    not_list = []
    for k,v in user_test.items():
        if user_label.has_key(k):
            if user_label[k] == v:
                count = count + 1
        else:
            not_list.append(k)

    return count,len(user_test),len(not_list)

def write_result(result):
    with open('./result/test_result.csv',  'wb') as f:
        writer = csv.writer(f)
        for i in range(0,len(result)):
            writer.writerow((result[i][0],result[i][1],result[i][2]))

if __name__ == '__main__':

    result = []
    for i in range(1,9):
        count,total,not_in = main(i)
        result.append([count,total,not_in])

    write_result(result)
            
