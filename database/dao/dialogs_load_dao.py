import logging
import traceback
import datetime
from peewee import OperationalError
from database.orm.dialogs_orm import Dialogs

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warning_logger = logging.getLogger("warning")


class DialogsDAO(object):

    @staticmethod
    def load_dialogs(start_time, end_time=datetime.datetime.now):
        try:
            dialogs = (Dialogs.select().where(
                (Dialogs.time >= start_time) & (Dialogs.time <= end_time)))
            return dialogs
        except OperationalError as operational_e:
            error_logger.error("从数据库读取对话时发生连接数据库错误, %s,%s", str(
                operational_e), traceback.format_exc(), extra={"host": 'localhost'})
            raise BaseException("连接数据库发生错误")
        except:
            error_logger.error("从数据库读取对话时发生其他错误, %s", traceback.format_exc(), extra={
                "host": 'localhost'})
            raise BaseException("从数据库读取对话时发生其他错误")

    @staticmethod
    def convert_dialogs_format(dialogs):
        """
        将peewee取出的对话转化为以下格式：
        {"id": [("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"), ("customer_service", "start_time", "end_time", "你是变态啊")]}
        """
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

    @staticmethod
    def convert_dialogs_repeat_call_format(dialogs):
        """
        将peewee取出的对话转化为以下格式：
        {"call_id": {"content":[("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"),
                                          ("customer_service", "start_time", "end_time", "你是变态啊")],
                     "user_id": ""
                     "time": datetime}
        }
        """
        result = {}
        for dialog in dialogs:
            dialog_id = dialog.call_id
            result[dialog_id] = {"content": [], "user_id": dialog.user_id, "time": dialog.time}

            for row in dialog.content.split('\n'):
                try:
                    target, start_time, end_time, sentence = row.split('\t')
                    result[dialog_id]["content"].append(
                        ("user" if target == '0' else "customer_service", start_time, end_time, sentence)
                    )
                except Exception:
                    pass
        return result
