# Created by Helic on 2018/7/29
import uuid
from .utils import *
from .tfidfTestSklearn import Tfidf


class SmartTextAnalyser:
    def __init__(self, analyser_id, matched_sentences, prob, target, analyser_type):
        """"""
        self.analyser_id = analyser_id
        self.matched_sentences = matched_sentences  # list
        self.prob = prob
        self.target = target
        self.analyser_type = analyser_type

    @classmethod
    def create(cls, matched_sentences, prob, target, analyser_type, host="localhost", port=3306, user="helic",
               passwd="root1234", db="zhongxin", charset="utf8"):
        """
        用户新建analyser,存入zhongxin.smart_text_analyser

        @:param
        matched_sentences: <string[]>，好多事啊回复的

        @:return
        <>.
        """
        try:
            analyser_id = str(uuid.uuid4())
            db, cursor = connect_to_db(host=host, port=port, user=user, passwd=passwd, db=db, charset="utf8")
            sql = "INSERT INTO smart_text_analyser(id, matched_sentences, prob, target, analyser_type) VALUES ('%s', '%s', %f, '%s', '%s')" % (
            analyser_id, matched_sentences, prob, target, analyser_type)
            print(sql)
            cursor.execute(sql)
            db.commit()
            return True
        except Exception:
            raise Exception("failed to create analyser from datebase")

    # @classmethod
    # def create(cls, matched_sentences, prob, target, analyser_type):
    #     """
    #     用户新建analyser,存入zhongxin.smart_text_analyser
    #     :param matched_sentences:
    #     :param prob:
    #     :param target:
    #     :param analyser_type:
    #     :return:
    #     """
    #
    #     pass
    # @classmethod
    # def load(cls, analyser_id, host="localhost", port=3306, user="helic", passwd="root1234", db="zhongxin",
    #          charset="utf8"):
    #     """从数据库中读取analyser_id对应的model,返回一个SmartTextAnalyser instance"""
    #     try:
    #         _, cursor = connect_to_db(host=host, port=port, user=user, passwd=passwd, db=db, charset="utf8")
    #         sql = "select * from smart_text_analyser where id = '%s'" % analyser_id
    #         cursor.execute(sql)
    #         results = cursor.fetchall()  # 数据库的每一项为一个元组
    #         analyser_id, matched_sentences, prob, target, analyser_type = results[0]
    #         matched_sentences = list(map(lambda x: x.strip(), matched_sentences.split('\n')))
    #         return cls(analyser_id, matched_sentences, prob, target, analyser_type)
    #     except Exception:
    #         raise Exception("failed to load analyser from datebase")

    @classmethod
    def load(cls, analyser_id, matched_sentences, prob, target, analyser_type):
        """返回一个SmartTextAnalyser instance"""
        matched_sentences = list(map(lambda x: x.strip(), matched_sentences.split('\n')))
        return cls(analyser_id, matched_sentences, prob, target, analyser_type)

    def test(self, dialogs):
        """
        针对于单个analyser做测试
        :param dialogs: {"id": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"), ("customer_service", "start_time", "end_time", "你是变态啊")]}
        :return  result: {
                            "0": {
                                "status": true,
                                "matched": [
                                    ["source_sentence", "matched_sentence", similarity]
                                ]
                            },
                            "1": {
                                "status": false,
                                "matched": []
                            }
                        }
        """
        tfidf = Tfidf()
        results = {}
        for dialog_id in dialogs:
            dialog = dialogs[dialog_id]
            results[dialog_id] = {"status": False, "matched": []}
            if self.target == "all":
                for sentence in dialog:
                    target, start_time, end_time, content = sentence
                    matched = tfidf.main(content, self.matched_sentences, value=self.prob)
                    if matched:
                        results[dialog_id]["status"] = True
                        matched = list(matched)
                        matched.insert(0, content)
                        results[dialog_id]["matched"].append(matched)
                    else:
                        continue
            elif self.target == "user":
                for sentence in dialog:
                    target, start_time, end_time, content = sentence
                    if target == "user":
                        matched = tfidf.main(content, self.matched_sentences, value=self.prob)
                        if matched:
                            results[dialog_id]["status"] = True
                            matched = list(matched)
                            matched.insert(0, content)
                            results[dialog_id]["matched"].append(matched)
                        else:
                            continue
                    else:
                        continue
            else:
                for sentence in dialog:
                    target, start_time, end_time, content = sentence
                    if target == "customer_service":
                        matched = tfidf.main(content, self.matched_sentences, value=self.prob)
                        if matched:
                            results[dialog_id]["status"] = True
                            matched = list(matched)
                            matched.insert(0, content)
                            results[dialog_id]["matched"].append(matched)
                        else:
                            continue
                    else:
                        continue

        return results


if __name__ == '__main__':
    dialogs = {"1": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"), ("customer_service", "start_time", "end_time", "你是变态啊")]}
    # SmartTextAnalyser.create(matched_sentences="就你这种人，送给我我都不要\n麻烦有多远滚多远，越快越好", prob=0.6, target="all",
    #                          analyser_type="测试")

    # analyser1 = SmartTextAnalyser.load(analyser_id=["11be6f1e-aa16-43d8-935b-e2be21fb8171"])
    # result = analyser1.test(dialogs=dialogs)
    # print(result, analyser1.analyser_type)
