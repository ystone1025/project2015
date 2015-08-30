#-*-coding=utf-8-*-

import os
import re
import sys
import json
import csv
import random
from find_users import get_friends, get_user
from domain_by_text import domain_classfiy_by_text
from global_utils import labels,zh_labels,txt_labels,re_cut

def readProtoUser():
    f = open("./protou_combine/protou.txt", "r")
    protou = dict()
    for line in f:
        area=line.split(":")[0]
        if area not in protou:
            protou[area]=set()
        for u in (line.split(":")[1]).split():
            protou[area].add(str(u))

    return protou

proto_users = readProtoUser()

def readTrainUser():

    txt_list = ['abroadadmin','abroadmedia','business','folkorg','grassroot','activer',\
                'homeadmin','homemedia','lawyer','mediaworker','politician','university']
    data = dict()
    for i in range(0,len(txt_list)):
        f = open("./domain_combine/%s.txt" % txt_list[i],"r")
        item = []
        for line in f:
            line = line.strip('\r\n')
            item.append(line)
        data[txt_list[i]] = set(item)
        f.close()

    return data

train_users = readTrainUser()

def user_domain_classifier_v1(friends, fields_value=txt_labels, protou_dict=proto_users):#根据用户的粉丝列表对用户进行分类
    mbr = {'university':0, 'homeadmin':0, 'abroadadmin':0, 'homemedia':0, 'abroadmedia':0, 'folkorg':0, 
          'lawyer':0, 'politician':0, 'mediaworker':0, 'activer':0, 'grassroot':0, 'other':0, 'business':0}
   
    # to record user with friends in proto users
    for f in friends:
        for area in fields_value:
            protous = protou_dict[area]
            if f in protous:
                mbr[area] += 1

    # for users no none friends in proto users,get their keywords
    if len(friends) == 0:
        # mbr = {"culture":0, "entertainment":0, "fashion":0,'education':0,"finance":0, "sports":0, "technology":0,'media':0}
        mbr['other'] += 1       

    count = 0
    for k,v in mbr.items():
        count = count + v

    if count == 0:
        return 'other'
    
    #print mbr
    sorted_mbr = sorted(mbr.iteritems(), key=lambda (k, v): v, reverse=True)
    field1 = sorted_mbr[0][0]

    return field1

def getFieldFromProtou(uid, protou_dict=train_users):#判断一个用户是否在种子列表里面

    result = 'Null'
    for k,v in protou_dict.items():
        if uid in v:
            return k

    return result

def domain_classfiy(uid_weibo,flag):#领域分类主函数
    '''
    用户领域分类主函数
    输入数据示例：
    uid_weibo:字典
    {uid1:[weibo1,weibo2,weibo3,...]}
    flag:是否有用户认证类型信息,数字
    1表示有，0表示没有

    输出数据示例：字典
    {uid1:{domain},uid2:{domain}...}
    '''

    weibo_text = dict()
    uidlist = []
    for k,v in uid_weibo.items():
        item = ''
        for i in range(0,len(v)):
            text = re_cut(v[i]['text'])
            item = item + ',' + text
        weibo_text[k] = item
        uidlist.append(k)
    
    users = get_user(uidlist)
    print 'len(users):',len(users)
    print len(uidlist)
    domain = dict()  

    for k,v in users.items():

        field = getFieldFromProtou(k, protou_dict=train_users)#判断uid是否在种子用户里面 

        if field != 'Null':#该用户在种子用户里面
            domain[str(k)] = zh_labels[labels.index(field)]
        else:
            uid = k
            if v == 'other':#没有任何背景信息
                row = []
                row.append(uid)
                f= get_friends(row)#返回用户的粉丝列表
                friends = f[str(uid)]
                if len(friends):
                    field = user_domain_classifier_v1(friends, fields_value=txt_labels, protou_dict=proto_users)
                    if field == 'other':#粉丝列表分不出来
                        field_dict = domain_classfiy_by_text({k: weibo_text[k]})#根据用户文本进行分类
                        field = field_dict[k]
                else:
                    field_dict = domain_classfiy_by_text({k: weibo_text[k]})#根据用户文本进行分类
                    field = field_dict[k]
                
            else:#有背景信息
                if flag == 1:#表示有背景信息
                    pass #需要写背景信息的接口
                else:
                    row = []
                    row.append(uid)
                    f= get_friends(row)#返回用户的粉丝列表
                    friends = f[str(uid)]
                    if len(friends):
                        field = user_domain_classifier_v1(friends, fields_value=txt_labels, protou_dict=proto_users)
                        if field == 'other':#粉丝列表分不出来
                            field_dict = domain_classfiy_by_text({k: weibo_text[k]})#根据用户文本进行分类
                            field = field_dict[k]
                    else:
                        field_dict = domain_classfiy_by_text({k: weibo_text[k]})#根据用户文本进行分类
                        field = field_dict[k]
                
            domain[str(uid)] = zh_labels[labels.index(field)]

    return domain

def test_data():#测试输入

    uid_weibo = dict()
    reader = csv.reader(file('./weibo_data/uid_text_0728.csv', 'rb'))
    for mid,w_text in reader:
        if uid_weibo.has_key(str(mid)):
            item = uid_weibo[str(mid)]
            item_dict = {'uid':mid,'text':w_text}
            item.append(item_dict)
            uid_weibo[str(mid)] = item
        else:
            item = []
            item_dict = {'uid':mid,'text':w_text}
            item.append(item_dict)
            uid_weibo[str(mid)] = item

    return uid_weibo

def rand_for_test(name,uid_weibo):
    
    rand_weibo = dict()
    for k,v in uid_weibo.items():#从所有已标注样本中随机抽取数据进行测试
        f = random.randint(1, 8)
        if f == name:
            rand_weibo[k] = v

    return rand_weibo

def write_file(domain,name):#将结果写入文件

    with open('./result/result%s.csv' % name, 'wb') as f:
        writer = csv.writer(f)
        for k,v in domain.items():
            writer.writerow((k,v))

if __name__ == '__main__':

    uid_weibo = test_data()
    for i in range(1,9):
        user_weibo = rand_for_test(i,uid_weibo)
        domain = domain_classfiy(user_weibo,0)
        write_file(domain,i)
    
    
