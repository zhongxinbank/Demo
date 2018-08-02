# Created by Helic on 2018/6/20
import os
import pymysql
import datetime
import json
import jieba


def safe_mkdir(path):
    """ Create a directory if there isn't one already. """
    try:
        os.mkdir(path)
    except OSError:  # 当目录已经存在时会抛出异常
        pass


def safe_mkdirs(path):
    """ Create a directory(多级目录) if there isn't one already. """
    try:
        os.makedirs(path)
    except OSError:  # 当目录已经存在时会抛出异常
        pass


def connectDB(host="localhost", port=3306, user="helic", passwd="root1234", db="zhongxin", charset="utf8"):
    """connect to mysql database"""
    db = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = db.cursor()
    return db, cursor


def insertDB(dic, db, cursor):
    """"""
    try:
        sql = '''INSERT into repeated_call_model(`logic_expression`, `time_interval`, `logic_relationship`) VALUES ("%s","%s","%s")''' % (
            dic["logic_expression"], dic["time_interval"], dic["logic_relationship"])
        cursor.execute(sql)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def selectDB(cursor):
    """"""
    sql = '''select * from repeated_call_model'''
    cursor.execute(sql)
    return cursor.fetchall()  # 数据库的每一项为一个元组


def selectDB_by_id(cursor, model_id):
    """"""
    sql = '''select * from repeated_call_model WHERE id=%d''' % model_id
    cursor.execute(sql)
    return cursor.fetchall()  # 数据库的每一项为一个元组


def deleteDB(db, cursor, id):
    """"""
    try:
        sql = '''DELETE FROM repeated_call_model WHERE id= %d''' % id
        cursor.execute(sql)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def updateDB(dic, db, cursor, id):
    """"""
    try:
        sql = '''update repeated_call_model set logic_expression="%s",time_interval=%d,logic_relationship="%s" WHERE id=%d''' % \
              (dic["logic_expression"], dic["time_interval"], dic["logic_relationship"], id)
        cursor.execute(sql)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def selectDB_with_time(cursor, time_start, time_end):
    """模拟测试，目前没有数据"""
    sql = '''select * from test WHERE created_time BETWEEN "%s" and "%s" ORDER BY created_time''' % (time_start, time_end)
    cursor.execute(sql)
    return cursor.fetchall()  # 数据库的每一项为一个元组


def convert_results_to_dialog(results):
    """将数据库的查询结果转化为特定格式
    Input:
        get_dialog_with_conditions()方法返回的results
    Output:
        {"dialog_id": [("agent", "time","content"), ("client", "time","content")]}
    """
    dialogs = [item[-1] for item in results]
    dialog_ids = [item[0] for item in results]
    output = {}
    for k, item in enumerate(dialogs):
        dialog = []
        for i in item.split('\n'):  # list
            if i != '':
                dialog.append(i.split('#', 2))
        dialog_id = dialog_ids[k]
        output[dialog_id] = dialog
    return output


def load_model(model_path):
    """从json文件中读取model"""
    with open(model_path, 'r', encoding='utf-8') as f:
        model = json.load(f)
    return model


def write_model(model_path, model):
    """向json文件写入model"""
    try:
        with open(model_path, 'w', encoding='utf-8') as f:
            model = json.dump(model, f, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_interval_time(time1, time2):
    """
    获取agent两次说话的间隔时间
            Input:
                   agent相邻两次说话的时间time1,time2
            Output；
                   间隔时间:interval_time (h）
    """
    # print("time1",time1)
    # print("time2", time2)
    t1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
    # print(t1, t2, t1 > t2)
    interval_time = (t2 - t1).seconds/3600 if t1 <= t2 else (t1 - t2).seconds/3600
    return interval_time


def convert_text_to_wordlist(text, cut_all_flag=False):
    """将文本转化为分词后的列表
    input:
        text: string
        cut_all_flag:如果cut_all=False，则会列出最优的分割选项；如果cut_all=True, 则会列出所有可能出现的词
    output:
        word_list: ['a', 'b']"""
    word_list = remove_stopwords(jieba.cut(text.strip(), cut_all=cut_all_flag))  # 分词
    return word_list


def get_stopwords(stopwords_path):
    """stopwords.txt文件中，每行放一个停用词，以\n分隔"""
    stopwords = []
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        for item in f.readlines():
            stopwords.append(item.strip())
    stopwords.extend(['，', '。', '？', '“', '”', '‘', '’', '；', '：', '！', '、', '（', '）', '-', '=',
                      '【', '】', ' ', '{', '}', ',', '.', '/', '\\', '(', ')', '?', '!', ';', ':', '\'',
                      '"', '[', ']', '~', '\n', '\t'])
    return set(stopwords)


def remove_stopwords(words):
    """去掉一些停用词和数字"""
    stopwords = get_stopwords(stopwords_path="VSM_model/stopwords.txt")
    new_words = []
    for i in words:
        if i in stopwords or i.isdigit():  # 去除停用词和数字
            continue
        else:
            new_words.append(i)
    return new_words