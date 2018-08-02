# message API
import json
import logging
import falcon
import traceback

from database.dao.action_log_dao import ActionLogDAO

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warining_logger = logging.getLogger("warning")


class TestResponder:
    
    def __init__(self):
        return
    
    def load(self):
        return 
        
    def on_get(self, req, res):
        try:
            ActionLogDAO.log_action(user_id="admin", action_type='development', action_name="测试服务器" ,action_status="成功", action_msg="成功测试服务器")
            res.status = falcon.HTTP_200
            res.body = json.dumps({
                "message": "Server Successfully Started",
                "status": {
                    "code" : 200,
                    "is_error": False,
                    "error_message": ""
                }
            }, ensure_ascii=False)
        except BaseException as e:
            error_logger.error("Test Responder 没有成功启动数据库和服务器, %s,%s", str(e), traceback.format_exc(), extra={"host":"localhost"})
            res.status = falcon.HTTP_400
            res.body = json.dumps({
                "message": "Server Failed",
                "status": {
                    "code" : 400,
                    "is_error": True,
                    "error_message": "没有成功启动数据库和服务器??"
                }
            }, ensure_ascii=False)