人物性格分类：
调用方法
根据情绪曲线分类：from test_ch_sentiment import classify_sentiment
根据情绪曲线分类：from test_ch_topic import classify_topic

输入：用户id列表，查询es的开始时间（字符串），查询es的结束时间（字符串），是否需要再计算情绪（int，1表示需要计算，0表示不需要计算）
输入样例：[uid1,uid2,uid3,...],'2013-09-01','2013-09-07',0
输出：字典  uid对应其性格类型
输出样例:{uid1:'冲动'，uid2:'抑郁'}

性格类型分类：
根据情绪分类：冲动、抑郁、未知
根据文本分类：批判、未知
