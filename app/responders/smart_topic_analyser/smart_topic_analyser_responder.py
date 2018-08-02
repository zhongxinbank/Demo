# message API
import json
import logging
import falcon
import traceback

from app.responders.smart_topic_analyser.utils import *
from database.dao.dialogs_load_dao import DialogsDAO
from database.dao.smart_topic_analyser_dao import SmartTopicAnalyserDAO
from app.responders.smart_topic_analyser.smart_topic_analyser import SmartTopicAnalyser

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warining_logger = logging.getLogger("warning")


class SmartTopicAnalyserResponder:

    def __init__(self):
        return

    def load(self):
        return

    def on_get(self, req, res):
        params = req.params
        if params["action"] == "test":
            result = self.test(start_time=params['start_time'], end_time=params["end_time"], analyser_id=params["analyser_id"] if "analyser_id" in params else None)
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "load_analyser":
            result = self.load_smart_topic_analyser(analyser_id=params["analyser_id"] if "analyser_id" in params else None)
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "create_analyser":
            result = self.create_smart_topic_analyser(params["matched_sentences"], float(params["prob"]), params["target"], params["analyser_type"])
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "modify_analyser":
            result = self.modify_smart_topic_analyser(analyser=params["analyser"])
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "delete_analyser":
            result = self.delete_smart_topic_analyser(analyser_id=params["analyser_id"])
            res.status = result["status"]
            res.body = result["body"]

    def test(self, start_time, end_time, analyser_id=None):
        """
        对analyser做测试,如果analyser_id为空，则测试所有的Sim analyser
        :param start_time:
        :param end_time:
        :param analyser_id:
        :return:
        """
        try:
            dialogs = DialogsDAO.load_dialogs(start_time=start_time, end_time=end_time)
            dialogs = DialogsDAO.convert_dialogs_format(dialogs)

            analysers = SmartTopicAnalyserDAO.load_smart_topic_analyser(analyser_id=analyser_id)
            result = {}
            for sim_topic_analyser in analysers:
                sim_topic_analyser = SmartTopicAnalyser.load(sim_topic_analyser.id,
                                                             sim_topic_analyser.matched_sentences,
                                                             sim_topic_analyser.prob, sim_topic_analyser.target,
                                                             sim_topic_analyser.analyser_type)
                result[sim_topic_analyser.analyser_type] = sim_topic_analyser.test(dialogs=dialogs)

            result = transform(result)

            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "SmartTopicAnalyser成功执行",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    },
                    "result": result
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("SmartTopicAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "SimAnalyser Server Failed",
                    "status": {
                        "code": 400,
                        "is_error": True,
                        "error_message": "没有成功启动数据库和服务器"
                    }
                }, ensure_ascii=False)
            }
            return res

    def load_smart_topic_analyser(self, analyser_id=None, analyser_type=None):
        """
        读取sim_topic_analyser   # TODO analyser_type
        :param analyser_id: list<string> => ["id1","id2",...]
        :return:
        """
        try:
            analysers = SmartTopicAnalyserDAO.load_smart_topic_analyser(analyser_id=analyser_id)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功查询SmartAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    },
                    "result": [(analyser.id, analyser.matched_sentences, analyser.prob, analyser.target, analyser.analyser_type) for analyser in analysers]
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("SmartTopicAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "查询SmartAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "查询SmartAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def create_smart_topic_analyser(self, matched_sentences, prob, target, analyser_type):
        """
        新建sim_topic_analyser
        :param matched_sentences: "sentence" + '\n' + "sentence"
        :param prob:
        :param target:
        :param analyser_type:
        :return:
        """
        try:
            SmartTopicAnalyserDAO.create_smart_topic_analyser(matched_sentences, prob, target, analyser_type)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功创建SmartTopicAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("SmartTopicAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "创建SimAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "创建SimAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def modify_smart_topic_analyser(self, analyser):     # TODO 同时修改多个analyser,如何解析GET params
        """
        修改sim_topic_analyser，存入数据库
        :param analyser: ["11be6f1e-aa16-43d8-935b-e2be21fb8171",
                            "你摸着自己良心我有说错吗\n你是变态啊",
                            0.7,
                            "all",
                            "辱骂指责"]
        :return:
        """
        try:
            SmartTopicAnalyserDAO.modify_smart_topic_analyser(analyser=analyser)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功修改SimAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("SmartTopicAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "修改SimAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "修改SimAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def delete_smart_topic_analyser(self, analyser_id):
        """
        删除smart_text_analyser
        :param analyser_id: list<string> => ["id1","id2",...]
        :return:
        """
        try:
            SmartTopicAnalyserDAO.delete_smart_topic_analyser(analyser_id=analyser_id)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功删除SmartAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("SmartTextAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "删除SmartAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "删除SmartAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res
