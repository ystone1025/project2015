#-*-coding=utf-8-*-
#vision2
import os
import re
import sys
import json
import csv
from config import abs_path

def input_data():#测试输入

    uid_weibo = dict()
    reader = csv.reader(file(abs_path+'/weibo_data/uid_text_0728.csv', 'rb'))
    for mid,w_text in reader:
        if uid_weibo.has_key(str(mid)):
            uid_weibo[str(mid)] = uid_weibo[str(mid)] + '-' + w_text
        else:
            uid_weibo[str(mid)] = w_text
    
    return uid_weibo
