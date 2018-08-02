# Created by Helic on 2018/8/2
import logging
import traceback
import uuid
from peewee import OperationalError
from database.orm.repeat_call_analyser_orm import RepeatCallAnalyser

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
warining_logger = logging.getLogger("warning")


class RepeatCallAnalyserDAO(object):

    @staticmethod
    def load_repeat_call_analyser(analyser_id=None):
        """
        从repeat_call_analyser table中根据analyser_id读取analyser

        :param analyser_id: list<string> => ["id1","id2",...]
        :return: 数据库返回的RepeatCallAnalyser instances
        """
        try:
            # analyser_ids = analyser_id.split(',')  # 自动转成list
            if analyser_id:
                if type(analyser_id) == str:  # 只输入单个analyser
                    analyser_id = [analyser_id]
                analysers = (RepeatCallAnalyser.select().where(RepeatCallAnalyser.id << analyser_id))
            else:
                analysers = (RepeatCallAnalyser.select())  # 如果没有analyser_id，默认查询所有analysers
            # info_logger.info("analyser_id:{}".format(analyser_id))
            return analysers
        except OperationalError as operational_e:
            error_logger.error("从zhongxin.repeat_call_analyser数据库读取analyser时发生连接数据库错误, %s,%s", str(
                operational_e), traceback.format_exc(), extra={"host": 'localhost'})
            raise BaseException("连接数据库发生错误")
        except:
            error_logger.error("从zhongxin.repeat_call_analyser数据库读取analyser时发生其他错误, %s", traceback.format_exc(), extra={
                "host": 'localhost'})
            raise BaseException("从zhongxin.repeat_call_analyser数据库读取analyser时发生其他错误")

    @staticmethod
    def create_repeat_call_analyser(matched_sentences, prob, analyser_type, description, time_interval, logic):
        """
        用户新建analyser,存入zhongxin.repeat_call_analyser

        :param
        :return bool
        """
        try:
            RepeatCallAnalyser.create(
                id=str(uuid.uuid4()),
                matched_sentences=matched_sentences,  # string
                prob=float(prob),
                analyser_type=analyser_type,
                description=description,
                time_interval=int(time_interval),
                logic=logic
            )
        except OperationalError as operational_e:
            error_logger.error("记录RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生连接数据库错误, %s,%s",
                               str(operational_e), traceback.format_exc(),
                               extra={"host": 'localhost'})
            raise BaseException("连接数据库发生错误")
        except:
            error_logger.error("记录RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生其他错误, %s", traceback.format_exc(),
                               extra={"host": 'localhost'})
            raise BaseException("连接数据库发生错误")

    @staticmethod
    def modify_repeat_call_analyser(analyser):
        """
        修改repeat_call_analyser，存入数据库
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
            RepeatCallAnalyser.update(matched_sentences=analyser[1], prob=float(analyser[2]), analyser_type=analyser[3],
                                      description=analyser[4], time_interval=int(analyser[5]), logic=analyser[6]).\
                                      where(RepeatCallAnalyser.id == analyser[0]).execute()
        except OperationalError as operational_e:
            error_logger.error("修改RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生连接数据库错误, %s,%s",
                               str(operational_e), traceback.format_exc(),
                               extra={"host": 'localhost'})
            raise BaseException("修改RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生连接数据库错误")
        except:
            error_logger.error("修改RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生其他错误, %s", traceback.format_exc(),
                               extra={"host": 'localhost'})
            raise BaseException("修改RepeatCallAnalyser到zhongxin.repeat_call_analyser数据库时发生其他错误")

    @staticmethod
    def delete_repeat_call_analyser(analyser_id):
        """
        从repeat_call_analyser table中根据analyser_id删除analyser

        :param analyser_id: list<string> => ["id1","id2",...]
        :return: 数据库返回的RepeatCallAnalyser instances
        """
        try:
            # analyser_ids = analyser_id.split(',')  # 自动转成list
            if type(analyser_id) == str:        # 只输入单个analyser
                analyser_id = [analyser_id]
            # info_logger.info("????:{}".format(analyser_id))
            RepeatCallAnalyser.delete().where(RepeatCallAnalyser.id << analyser_id).execute()
        except OperationalError as operational_e:
            error_logger.error("从zhongxin.repeat_call_analyser数据库删除analyser时发生连接数据库错误, %s,%s", str(
                operational_e), traceback.format_exc(), extra={"host": 'localhost'})
            raise BaseException("连接数据库发生错误")
        except:
            error_logger.error("从zhongxin.repeat_call_analyser数据库删除analyser时发生其他错误, %s", traceback.format_exc(), extra={
                "host": 'localhost'})
            raise BaseException("从zhongxin.repeat_call_analyser数据库删除analyser时发生其他错误")

