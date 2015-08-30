# -*- coding: UTF-8 -*-
'''
the common function of searching user profile
'''
from elasticsearch.exceptions import NotFoundError
from global_utils import es_user_profile as es


INDEX_NAME = 'weibo_user'
DOC_TYPE = 'user'


# 自定义查询
def es_get_source(id):
    try:
        source = es.get_source(index=INDEX_NAME, doc_type=DOC_TYPE, id=id)
    except NotFoundError as e:
        source = {}
    except Exception as e:
        # TODO handle exception
        raise e
    return source

