# main.py

'''
Initialize Settings From Server, loading logging settings, and check or create folder to store local log files
'''
import json
import logging
import logging.config
import os
logger_config = json.load(open('./logger_config.json'), encoding='utf-8')
if not os.path.exists('./log'):
    os.makedirs('./log')
logging.config.dictConfig(logger_config)
info_logger = logging.getLogger('info')
error_logger = logging.getLogger('error')
warning_logger = logging.getLogger('warning')


'''
Loading Python Modules
'''
import falcon

'''
Loading All Responder Modules
'''
from app.responders.test_responder import TestResponder
from app.responders.run_analysers_responder import AnalyserResponder
from app.responders.smart_text_analyser.smart_text_analyser_responder import SmartTextAnalyserResponder
from app.responders.smart_topic_analyser.smart_topic_analyser_responder import SmartTopicAnalyserResponder
from app.responders.repeat_call.repeat_call_analyser_reponder import RepeatCallResponder

test_responder = TestResponder()
smart_text_analyser_responder = SmartTextAnalyserResponder()
smart_topic_analyser_responder = SmartTopicAnalyserResponder()
repeat_call_analyser_responder = RepeatCallResponder()
analyser_responder = AnalyserResponder()
'''
Adding Routers & Responders
'''
api = falcon.API(media_type='application/json', middleware=[])
api.add_route('/test', test_responder)
api.add_route('/smart_text_analyser', smart_text_analyser_responder)
api.add_route('/smart_topic_analyser', smart_topic_analyser_responder)
api.add_route("/repeat_call_analyser", repeat_call_analyser_responder)
api.add_route("/run_analyser", analyser_responder)

info_logger.info("Ellison服务器完成初始化", extra={"host": 'localhost'})
app = api
