# Created by Helic on 2018/8/1
import json
import logging
import falcon
import traceback
import datetime

from database.dao.dialogs_load_dao import DialogsDAO
from database.dao.smart_text_analyser_dao import SmartTextAnalyserDAO
from app.responders.smart_text_analyser.smart_text_analyser import SmartTextAnalyser

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warining_logger = logging.getLogger("warning")


class AnalyserResponder:
    def __init__(self):
        return

    def load(self):
        pass

    def on_get(self, req, res):
        params = req.params
        if params['action'] == "run":
            result = self.run(config_path=params["config_path"] if "config_path" in params else "app/responders/config.json",
                              start_time=params["start_time"] if "start_time" in params else datetime.datetime.now() - datetime.timedelta(days=7),
                              end_time=datetime.datetime.now())
            res.status = result["status"]
            res.body = result["body"]

    @staticmethod
    def run(config_path="app/responders/config.json",
            start_time=datetime.datetime.now() - datetime.timedelta(days=7),
            end_time=datetime.datetime.now()):
        """ # TODO
        run config.json的所有analysers，默认是一周内的数据
        :param config_path
        :param start_time
        :param end_time
        :return
        """
        dialogs = DialogsDAO.load_dialogs(start_time=start_time, end_time=end_time)
        dialogs = DialogsDAO.convert_dialogs_format(dialogs)

        with open(config_path, 'r', encoding="utf-8") as f:
            config = json.load(f)

            results = {
                "SmartTextAnalyser": {},
                "RegexTextAnalyser": {},
                "TopicAnalyser": {},
                "EmotionAnalyser": {}
            }

            try:
                smart_analyser_ids = config["SmartTextAnalyser"]  # TODO 添加后续analyser
                analysers = SmartTextAnalyserDAO.load_smart_text_analyser(analyser_id=smart_analyser_ids)
                for analyser in analysers:
                    smart_text_analyser = SmartTextAnalyser.load(analyser.id, analyser.matched_sentences, analyser.prob,
                                                                 analyser.target, analyser.analyser_type)
                    results["SmartTextAnalyser"][smart_text_analyser.analyser_id] = smart_text_analyser.test(
                        dialogs=dialogs)
                res = {
                    "status": falcon.HTTP_200,
                    "body": json.dumps({
                        "message": "Analyser成功执行",
                        "status": {
                            "code": 200,
                            "is_error": False,
                            "error_message": ""
                        },
                        "result": results
                    }, ensure_ascii=False),

                }
                return res
            except BaseException as e:
                error_logger.error("AnalyserResponder 没有成功启动数据库和服务器, %s,%s", str(
                    e), traceback.format_exc(), extra={"host": "localhost"})
                res = {
                    "status": falcon.HTTP_400,
                    "body": json.dumps({
                        "message": "Analyser Server Failed",
                        "status": {
                            "code": 400,
                            "is_error": True,
                            "error_message": "没有成功启动数据库和服务器"
                        }
                    }, ensure_ascii=False)
                }
                return res



