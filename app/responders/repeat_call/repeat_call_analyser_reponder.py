import json
import logging
import falcon
import traceback

from database.dao.dialogs_load_dao import DialogsDAO
from database.dao.repeat_call_analyser_dao import RepeatCallAnalyserDAO
from app.responders.repeat_call.repeat_call_analyser import RepeatCallAnalyser

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warining_logger = logging.getLogger("warning")


class RepeatCallResponder:

    def __init__(self):
        return

    def load(self):
        return

    def on_get(self, req, res):
        params = req.params
        if params["action"] == "test":
            result = self.test(start_time=params['start_time'], end_time=params["end_time"],
                               analyser_id=params["analyser_id"] if "analyser_id" in params else None)
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "load_analyser":
            result = self.load_repeat_call_analyser(
                analyser_id=params["analyser_id"] if "analyser_id" in params else None)
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "create_analyser":
            result = self.create_repeat_call_analyser(params["matched_sentences"], float(params["prob"]),
                                                      params["analyser_type"], params["description"],
                                                      int(params["time_interval"]), params["logic"])
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "modify_analyser":
            result = self.modify_repeat_call_analyser(analyser=params["analyser"])
            res.status = result["status"]
            res.body = result["body"]
        elif params["action"] == "delete_analyser":
            result = self.delete_repeat_call_analyser(analyser_id=params["analyser_id"])
            res.status = result["status"]
            res.body = result["body"]

    def test(self, start_time, end_time, analyser_id=None):
        """
        对analyser做测试,如果analyser_id为空，则测试所有的repeat_call_analyser
        :param start_time:
        :param end_time:
        :param analyser_id:
        :return:
        """
        try:
            dialogs = DialogsDAO.load_dialogs(start_time=start_time, end_time=end_time)
            dialogs = DialogsDAO.convert_dialogs_repeat_call_format(dialogs)

            analysers = RepeatCallAnalyserDAO.load_repeat_call_analyser(analyser_id=analyser_id)
            result = {}
            for analyser in analysers:
                analyser = RepeatCallAnalyser.load(analyser.id, analyser.matched_sentences, analyser.prob,
                                                   analyser.analyser_type, analyser.description,
                                                   analyser.time_interval, analyser.logic)
                result[analyser.analyser_id] = analyser.test(dialogs=dialogs)

            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "RepeatCallAnalyser成功执行",
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
            error_logger.error("RepeatCallAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "RepeatCallAnalyser Server Failed",
                    "status": {
                        "code": 400,
                        "is_error": True,
                        "error_message": "没有成功启动数据库和服务器"
                    }
                }, ensure_ascii=False)
            }
            return res

    def load_repeat_call_analyser(self, analyser_id=None):
        """
        读取repeat_call_analyser
        :param analyser_id: list<string> => ["id1","id2",...]
        :return:
        """
        try:
            analysers = RepeatCallAnalyserDAO.load_repeat_call_analyser(analyser_id=analyser_id)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功查询RepeatCallAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    },
                    "result": [(analyser.id, analyser.matched_sentences, analyser.prob, analyser.analyser_type,
                                analyser.description, analyser.time_interval, analyser.logic) for analyser in analysers]
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("RepeatCallAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "查询RepeatCallAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "查询RepeatCallAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def create_repeat_call_analyser(self, matched_sentences, prob, analyser_type, description, time_interval, logic):
        """
        新建repeat_call_analyser
        :param matched_sentences: "sentence" + '\n' + "sentence"
        :param prob:
        :param analyser_type:
        :param description
        :param time_interval
        :param logic
        :return:
        """
        try:
            RepeatCallAnalyserDAO.create_repeat_call_analyser(matched_sentences, prob, analyser_type, description, time_interval, logic)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功创建RepeatCallAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("RepeatCallAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "创建RepeatCallAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "创建RepeatCallAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def modify_repeat_call_analyser(self, analyser):  # TODO 同时修改多个analyser,如何解析GET params
        """
        修改smart_text_analyser，存入数据库
        :param analyser: ["11be6f1e-aa16-43d8-935b-e2be21fb8171",
                            "你摸着自己良心我有说错吗\n你是变态啊",
                            0.7,
                            "重复来电",
                            "重复来电",
                            6,
                            "and"]
        :return:
        """
        try:
            RepeatCallAnalyserDAO.modify_repeat_call_analyser(analyser=analyser)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功修改RepeatCallAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("RepeatCallAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "修改RepeatCallAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "修改RepeatCallAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res

    def delete_repeat_call_analyser(self, analyser_id):
        """
        删除smart_text_analyser
        :param analyser_id: list<string> => ["id1","id2",...]
        :return:
        """
        try:
            RepeatCallAnalyserDAO.delete_repeat_call_analyser(analyser_id=analyser_id)
            res = {
                "status": falcon.HTTP_200,
                "body": json.dumps({
                    "message": "成功删除RepeatCallAnalyser",
                    "status": {
                        "code": 200,
                        "is_error": False,
                        "error_message": ""
                    }
                }, ensure_ascii=False)
            }
            return res
        except BaseException as e:
            error_logger.error("RepeatCallAnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                e), traceback.format_exc(), extra={"host": "localhost"})
            res = {
                "status": falcon.HTTP_400,
                "body": json.dumps({
                    "message": "删除RepeatCallAnalyser失败",
                    "status": {
                        "code": 400,
                        "is_error": False,
                        "error_message": "删除RepeatCallAnalyser失败"
                    }
                }, ensure_ascii=False)
            }
            return res
