#-*-coding=utf-8-*-

import os
import re
import sys
import json
import csv
import random
from find_users import get_friends, get_user
from domain_by_text import domain_classfiy_by_text
from global_utils import labels,zh_labels,txt_labels,re_cut,read_by_xapian,r_labels,xs
from user_domain import user_domain_classifier_v2

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
        return 'other',mbr
    
    sorted_mbr = sorted(mbr.iteritems(), key=lambda (k, v): v, reverse=True)
    field1 = sorted_mbr[0][0]

    return field1,mbr

def getFieldFromProtou(uid, protou_dict=train_users):#判断一个用户是否在种子列表里面

    result = 'Null'
    for k,v in protou_dict.items():
        if uid in v:
            return k

    return result

def get_recommend_result(v_type,label):#根据三种分类结果选出一个标签

    if v_type == 'other':#认证类型字段走不通
        if label[0] != 'other':
            return label[0]
        else:
            return label[2]

    if label[1] in r_labels:#在给定的类型里面分出来的身份
        return label[1]

    if label[1] == 'politician' and v_type == 1:
        return label[1]

    if label[1] == 'activer' and (v_type == 220 or v_type == 200):
        return label[1]

    if label[1] == 'other' and v_type == 400:
        return label[1]

    if label[0] != 'other':#根据粉丝结构分出来身份
        return label[0]
    else:
        return label[2]

def domain_classfiy(uid_weibo):#领域分类主函数
    '''
    用户领域分类主函数
    输入数据示例：
    uid_weibo:字典
    {uid1:[weibo1,weibo2,weibo3,...]}

    输出数据示例：
    domain：标签字典
    {uid1:[label1,label2,label3],uid2:[label1,label2,label3]...}
    注：label1是根据粉丝结构分类的结果，label2是根据认证类型分类的结果，label3是根据用户文本分类的结果

    re_label：推荐标签字典
    {uid1:label,uid2:label2...}
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
    r_domain = dict()
    text_result = dict()
    user_result = dict()
    for k,v in users.items():

        uid = k
        result_label = []
        sorted_mbr = dict()
        field1 = getFieldFromProtou(k, protou_dict=train_users)#判断uid是否在种子用户里面
        if field1 != 'Null':#该用户在种子用户里面
            result_label.append(field1)
        else:
            f= get_friends([k])#返回用户的粉丝列表
            friends = f[str(uid)]
            if len(friends):
                field1,sorted_mbr = user_domain_classifier_v1(friends, fields_value=txt_labels, protou_dict=proto_users)
            else:
                field1 = 'other'
                sorted_mbr = {'university':0, 'homeadmin':0, 'abroadadmin':0, 'homemedia':0, 'abroadmedia':0, 'folkorg':0, \
          'lawyer':0, 'politician':0, 'mediaworker':0, 'activer':0, 'grassroot':0, 'other':0, 'business':0}
            result_label.append(field1)
        
        r = read_by_xapian(xs,uid)
        if r == 'other':
            field2 = 'other'
        else:
            field2 = user_domain_classifier_v2(r)
        result_label.append(field2)

        field_dict,result = domain_classfiy_by_text({k: weibo_text[k]})#根据用户文本进行分类
        field3 = field_dict[k]
        result_label.append(field3)
                
        domain[str(uid)] = result_label
        user_result[str(uid)] = sorted_mbr#有问题
        text_result[str(uid)] = result[k]#有问题

        if r == 'other':
            re_label = get_recommend_result('other',result_label)#没有认证类型字段
        else:
            re_label = get_recommend_result(r['verified_type'],result_label)

        r_domain[str(uid)] = re_label
    
    return domain,re_label

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
            writer.writerow((k,zh_labels[labels.index(v[0])],zh_labels[labels.index(v[1])],zh_labels[labels.index(v[2])]))

def get_uid(name):

    uid_weibo = dict()
    reader = csv.reader(file('./weibo_data/%s.csv' % name, 'rb'))
    for mid,text in reader:
        mid = mid.strip('\xef\xbb\xbf')
        if not uid_weibo.has_key(str(mid)):
            uid_weibo[str(mid)] = text
    
    return uid_weibo

def get_test_user(uid_list,uid_weibo):
    
    rand_weibo = dict()
    for k,v in uid_weibo.items():#从所有已标注样本中随机抽取数据进行测试
        if uid_list.has_key(k):
            rand_weibo[k] = v

    return rand_weibo

def write_result(result_dict,name):#将结果写入文件(主要是针对粉丝结构以及微博文本分类的每一类的概率)
    
    with open('./result/result%s.csv' % name, 'wb') as f:
        writer = csv.writer(f)
        for k,v in result_dict.items():
            row = []
            row.append(k)
            if name == 'text':
                for i in range(0,len(v)):
                    row.append(str(v[i][0])+'*'+str(v[i][1]))
            else:
                print v
                for k1,v1 in v.items():
                    row.append(str(k1)+'*'+str(v1))
            writer.writerow((row))

if __name__ == '__main__':

    uid_weibo = test_data()
    uid_list = get_uid('222')
    user_weibo = get_test_user(uid_list,uid_weibo)
    domain,re_label = domain_classfiy(user_weibo)
    print re_label
##    write_file(domain,'222')
##    write_result(text_result,'text')
##    write_result(user_result,'user')
    
