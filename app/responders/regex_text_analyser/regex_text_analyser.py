# Created by Helic on 2018/7/31
import uuid
from .utils import *


class RegexTextAnalyser:
    def __init__(self, analyser_id, keywords, target, logic, analyser_type):
        """"""
        self.analyser_id = analyser_id
        self.keywords = keywords  # list
        self.target = target
        self.logic = logic
        self.analyser_type = analyser_type

    @classmethod
    def create(cls, keywords, target, logic, analyser_type, host="localhost", port=3306, user="helic",
               passwd="root1234", db="zhongxin", charset="utf8"):
        """
        用户新建analyser,存入zhongxin.regex_text_analyser
        :param
        :return
        """
        try:
            analyser_id = str(uuid.uuid4())
            db, cursor = connect_to_db(host=host, port=port, user=user, passwd=passwd, db=db, charset="utf8")
            sql = "INSERT INTO regex_text_analyser(id, keywords, target, logic, analyser_type) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s')" % (analyser_id, keywords, target, logic, analyser_type)
            # print(sql)
            cursor.execute(sql)
            db.commit()
            return True
        except Exception:
            raise Exception("failed to insert regex analyser to datebase")

    @classmethod
    def load(cls, analyser_id, host="localhost", port=3306, user="helic", passwd="root1234", db="zhongxin", charset="utf8"):
        """从数据库中读取analyser_id对应的model,返回一个RegexTextAnalyser instance"""
        try:
            _, cursor = connect_to_db(host=host, port=port, user=user, passwd=passwd, db=db, charset="utf8")
            sql = "select * from regex_text_analyser where id = '%s'" % analyser_id
            cursor.execute(sql)
            results = cursor.fetchall()  # 数据库的每一项为一个元组
            analyser_id, keywords, target, logic, analyser_type = results[0]
            keywords = keywords.split('，')
            return cls(analyser_id, keywords, target, logic, analyser_type)
        except Exception:
            raise Exception("failed to load analyser from datebase")

    @classmethod
    def load1(cls, analyser_id, matched_sentences, prob, target, analyser_type):
        """返回一个SmartTextAnalyser instance"""
        matched_sentences = list(map(lambda x: x.strip(), matched_sentences.split('\n')))
        return cls(analyser_id, matched_sentences, prob, target, analyser_type)

    # def test(self, dialogs):
    #     """
    #     针对于单个analyser做测试
    #     :param dialogs: {"id": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"), ("customer_service", "start_time", "end_time", "你是变态啊")]}
    #     :return result: {
    #                         "0": {
    #                             "status": true,
    #                             "matched": [
    #                                 ["matched_keywords", "matched_sentence"]
    #                             ]
    #                         },
    #                         "1": {
    #                             "status": false,
    #                             "matched": []
    #                         }
    #                     }
    #     """
    #     results = {}
    #     for dialog_id in dialogs:
    #         dialog = dialogs[dialog_id]
    #         results[dialog_id] = {"status": False, "matched": []}
    #         if self.target == "all":
    #             for sentence in dialog:
    #                 target, start_time, end_time, content = sentence
    #                 matched_words = [word for word in self.keywords if word in content]
    #                 if self.logic == 'or':
    #                     matched = '，'.join(matched_words)
    #                 else:
    #                     matched = '，'.join(matched_words) if len(matched_words) == len(self.keywords) else
    #                 if matched:
    #                     results[dialog_id]["status"] = True
    #                     results[dialog_id]["matched"].append([matched, content])
    #                 else:
    #                     continue
    #         elif self.target == "user":
    #             for sentence in dialog:
    #                 target, start_time, end_time, content = sentence
    #                 if target == "user":
    #                     matched = '，'.join([word for word in self.keywords if word in content])
    #                     if matched:
    #                         results[dialog_id]["status"] = True
    #                         results[dialog_id]["matched"].append([matched, content])
    #                     else:
    #                         continue
    #                 else:
    #                     continue
    #         else:
    #             for sentence in dialog:
    #                 target, start_time, end_time, content = sentence
    #                 if target == "customer_service":
    #                     matched = '，'.join([word for word in self.keywords if word in content])
    #                     if matched:
    #                         results[dialog_id]["status"] = True
    #                         results[dialog_id]["matched"].append([matched, content])
    #                     else:
    #                         continue
    #                 else:
    #                     continue
    #
    #     return results


if __name__ == '__main__':
    dialogs = {"1": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"),
                     ("customer_service", "start_time", "end_time", "你好啊")]}
    # RegexTextAnalyser.create(keywords="你好，世界", target="all", logic="or", analyser_type="测试")

    analyser1 = RegexTextAnalyser.load(analyser_id="b8c6b741-59ce-4d93-a276-ca9c14d3fa80")
    result = analyser1.test(dialogs=dialogs)
    print(result, analyser1.analyser_type)
