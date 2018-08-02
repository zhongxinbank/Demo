# Created by Helic on 2018/7/29
import pymysql
import copy


def connect_to_db(host="localhost", port=3306, user="helic", passwd="root1234", db="zhongxin", charset="utf8"):
    try:
        db = pymysql.connect(host=host, port=port, user=user,
                             passwd=passwd, db=db, charset="utf8")
        cursor = db.cursor()
        return db, cursor
    except Exception:
        raise Exception("failed to connect to datebase")


def convert_dialogs_format(dialogs):
    """将peewee取出的对话转化为以下格式： {"id": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"), ("customer_service", "start_time", "end_time", "你是变态啊")]"""
    result = {}
    for dialog in dialogs:
        dialog_id = dialog.call_id
        result[dialog_id] = []

        for row in dialog.content.split('\n'):
            try:
                target, start_time, end_time, sentence = row.split('\t')
                result[dialog_id].append(
                    ("user" if target == '0' else "customer_service", start_time, end_time, sentence)
                )
            except Exception:
                pass
    return result


def to_list(result):
    matched = []
    dialog_matched = []
    for analyser_type in result:
        for dialog_id in result[analyser_type]:
            if result[analyser_type][dialog_id]['status'] == True:
                matched.append([dialog_id, result[analyser_type][dialog_id]['matched'][0][0],
                                result[analyser_type][dialog_id]['matched'][0][2], analyser_type])
    return matched


def list_to_dict(matched):
    index = {}
    dialog_ids = []
    for item in matched:
        dialog_id = item[0]
        sentence = item[1]
        value = item[2]
        analyser_type = item[3]
        if not dialog_id in dialog_ids:
            dialog_ids.append(dialog_id)
            index[dialog_id] = []
        index[dialog_id].append([sentence, value, analyser_type])
        # dialog_matched.append(dict(dialog_id=dialog_id, matched=dict(sentence=sentence, value=value, analyser_type=analyser_type)))
    return index


def de_duplicate(result):
    new_result = copy.deepcopy(result)
    for item in result:
        for i in range(len(result)):
            if not item == result[i]:
                if item[0] == result[i][0]:
                    if item[1] > result[i][1]:
                        new_result.remove(result[i])
    return new_result


def remove_label(result):
    for item in result:
        result[item] = de_duplicate(result[item])
    return result


def transform(result):
    result = to_list(result)
    result = list_to_dict(result)
    result = remove_label(result)
    return result


if __name__ == '__main__':
    result = {'如何申请': {'1': {'status': True, 'matched': [['要怎么申请银行卡,有哪些类型的卡', '要怎么申请银行卡', 0.83443855366124]]},
                       '2': {'status': False, 'matched': []}},
              '卡类介绍': {'1': {'status': True, 'matched': [['要怎么申请银行卡,有哪些类型的卡', '有哪些类型的卡', 0.99443855366124]]},
                       '2': {'status': True, 'matched': [['我办的是什么类型的卡呢', '我办的是什么类型的卡呢', 1.0]]}},
              '办卡': {'1': {'status': True, 'matched': [['请问这边办卡需要带什么证件', '请问这边办卡需要带什么证件', 1.0]]},
                     '2': {'status': False, 'matched': []}}}
    result = transform(result)
    print(result)
