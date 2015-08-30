#!/usr/bin/env python
#-*-coding:utf-8-*-
from operator import itemgetter, attrgetter  
import datetime
import json
import sys

def readUidByArea(area):
    uidlist = []
    with open("./domain_combine/" + area + ".txt") as f:
        for line in f:
            uid = line.split()[0]
            uidlist.append(uid)
    return uidlist

def readFriendsByArea(area):
    user_friends_dict = dict()
    f = open('./dogapi_combine/'+area+'_friends.jl')
    for line in f:
        user = json.loads(line.strip())
        user_friends_dict[str(user['id'].encode('utf-8'))] = user['friends']
    f.close()
    return user_friends_dict

def protou_main():#主函数：根据种子用户及其粉丝结构，形成训练用户

    print 'start:'
    print datetime.datetime.now()
    classes = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'business']
    
    ####generate seed set
    seed={}##seed users
    pool={}##proto-user pool,get from seed users's friends
    # cls_seed=[]##class seed user
    su_cls={}##dictionary of seed user class
    n_s=0##number of seed users in each class
    foccur_all={}##total count of emerge
    friends=set()##all friends set of seed users
    error=0

    for area in classes:
        ###initialize
        su=set()##seed user for each class
        foccur_cls={}##count of emerge in current area

        uidlist = readUidByArea(area)
        ufriends = readFriendsByArea(area)
        for uid in uidlist:
            su.add(uid)
            su_cls[uid]=area
            try:
                for f in ufriends[uid]:
                    friends.add(f)
                    if f in foccur_all:
                        foccur_all[f] +=1
                    else:
                        foccur_all[f]=1
                    if f in foccur_cls:
                        foccur_cls[f] +=1
                    else:
                        foccur_cls[f]=1
            except:
                error +=1
                continue
        pool[area]=foccur_cls
        seed[area]=su
    print 'number of errors:%d'%error

    ####generate proto set
    
    ###sort pool users for each class
    s_cu={}
    for area in pool:
        lst=[]
        print area
        for f in pool[area]:
            c_count=pool[area][f]##count of f in current class
            a_count=foccur_all[f]##count of f in all
            score=(c_count*1.0)/a_count
            pair=tuple([f,score])
            lst.append(pair)
        s_cu[area]=sorted(lst,key=itemgetter(1),reverse=True)
    
    ###pick topN users from pool users and conbine with seed users as proto users for each class
    pu_cls={}
    topN=200

    for area in s_cu:
        u_count=0
        lst=set()
        for p in s_cu[area]:
            u_count +=1
            if u_count<=topN:
                lst.add(p[0])
                if p[0] not in su_cls:
                    su_cls[p[0]]=area
        for u in seed[area]:
            lst.add(u)
        pu_cls[area]=lst
        print area+str(len(s_cu[area]))##num of pool users
        print area+str(len(seed[area]))##num of seed users
        print area+str(len(pu_cls[area]))##num of proto users
    ###save proto users
    protou=open('./protou_combine/protou.txt','w')
    count=0
    for area in pu_cls:
        count +=1
        if count==1:
            incount=0
            protou.write(area+':')
            for u in pu_cls[area]:
                incount +=1
                if incount==1:
                    protou.write(str(u))
                else:
                    protou.write(' '+str(u))
        else:
            incount=0
            protou.write('\n'+area+':')
            for u in pu_cls[area]:
                incount +=1
                if incount==1:
                    protou.write(str(u))
                else:
                    protou.write(' '+str(u))
    print 'end:'
    print datetime.datetime.now()

if __name__ == '__main__':

    protou_main()
    
