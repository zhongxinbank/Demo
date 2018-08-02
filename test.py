from falcon import testing
from database.dao.model_dao import ModelDAO
from database.orm.model_orm import ModelORM
from database.orm.message_orm import MessageORM
import time, traceback

import os
from main import api
import unittest, logging, json, uuid

info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
warning_logger = logging.getLogger('warning_logger')

test_user_id = str(uuid.uuid4())
test_transaction_id = str(uuid.uuid4())

basic_post_body = {
    "user_id": test_user_id,
    "transaction_id": test_transaction_id,
    "time_zone": "Asia/Shanghai"
}

global SHARED_STORAGE_PATH
SHARED_STORAGE_PATH = os.environ['SHARED_STORAGE_PATH']

class MyTestCase(testing.TestCase):
    curr_model_config = None

    def setUp(self):
        super(MyTestCase, self).setUp()
        curr_model = None
        if os.environ["MODE"] == "SIMULATION":
            curr_model = ModelDAO.find_curr_simulating_model()
        else:
            curr_model = ModelDAO.find_curr_deployed_model()
        self.curr_model_config = json.loads(curr_model["config"], encoding='utf-8')
        self.app = api

def find_latest_msg_record(user_id):
    msg_record = list(MessageORM.select().where(MessageORM.user_id==user_id).order_by(MessageORM.created_at).execute())[-1]
    return msg_record


class TestMyApp(MyTestCase):
    def test010_welcome_message(self):
        try:
            info_logger.info("开始测试WelcomeMessage")
            result = self.simulate_post('/chatbot/welcome', json=basic_post_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['bot_message']['msg_content']['plain_response'], self.curr_model_config['static_msg']['welcome_msg'])
            self.assertEqual(result.json['bot_message']['survey_enabled'], False)

            #开始验证db信息
            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.model_id, self.curr_model_config['model_id'])
            self.assertEqual(latest_msg_record.user_msg, '')
            self.assertEqual(latest_msg_record.user_res_type, 'text')
            self.assertEqual(latest_msg_record.bot_msg, json.dumps({"plain_response": result.json['bot_message']['msg_content']['plain_response']}, ensure_ascii=False))
            self.assertEqual(latest_msg_record.ques_cat, '')
            self.assertEqual(latest_msg_record.survey_enabled, False)
            self.assertEqual(latest_msg_record.survey_grade, -1)
            self.assertEqual(latest_msg_record.survey_feedback, '')
            info_logger.info("成功测试WelcomeMessage")
        except BaseException as e:
            info_logger.error("WelcomeMessage测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            raise BaseException("WelcomeMessage测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            


    def test020_regex_message(self):
        try: 
            info_logger.info("Start Testing Regexp Message Chat")
            post_body = basic_post_body.copy()
            post_body['user_message'] = {
                "text": "帮我激活一张卡片"
            }
            result = self.simulate_post('/chatbot/message', json=post_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['bot_message']['msg_content']['plain_response'], {
                "text": "快速激活卡片", 
                "navigation": {
                    "ios_addr": "ctrl://openCard{\"eventID\":\"300008\"}",
                    "android_addr": "ctrl://openCard{\"eventID\":\"300009\"}",
                    "app_v_start": "4.0.0",
                    "app_v_end": "8.0.0",
                    "default": self.curr_model_config['navigation_default_msg']
                }
            })
            #开始验证db信息
            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.model_id, self.curr_model_config['model_id'])
            self.assertEqual(latest_msg_record.user_msg, '帮我激活一张卡片')
            self.assertEqual(latest_msg_record.user_res_type, 'text')
            self.assertEqual(latest_msg_record.bot_msg, json.dumps({"plain_response": {
                "text": "快速激活卡片", 
                "navigation": {
                    "ios_addr": "ctrl://openCard{\"eventID\":\"300008\"}",
                    "android_addr": "ctrl://openCard{\"eventID\":\"300009\"}",
                    "app_v_start": "4.0.0",
                    "app_v_end": "8.0.0",
                    "default": self.curr_model_config['navigation_default_msg']
                }
            }}, ensure_ascii=False))
            self.assertEqual(latest_msg_record.ques_cat, '开卡')
            self.assertEqual(latest_msg_record.survey_enabled, self.curr_model_config['survey']['function_enabled'])
            self.assertEqual(latest_msg_record.survey_grade, -1)
            self.assertEqual(latest_msg_record.survey_feedback, '')
            info_logger.info("成功测试RegexMessage")
        except BaseException as e:
            info_logger.error("RegexMessage测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            raise BaseException("RegexMessage测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())

    def test021_low_freq_message(self):
        try:
            low_freq_qas_file = open(os.path.join(SHARED_STORAGE_PATH, self.curr_model_config['model_id'], 'low_freq_qas.json'), "r", encoding='utf-8')
            low_freq_qas_data = json.load(low_freq_qas_file)
            for question in low_freq_qas_data:
                post_body = basic_post_body.copy()
                post_body['user_message'] = {
                    "text": question
                }
                result = self.simulate_post('/chatbot/message', json=post_body)
                self.assertEqual(result.json['status']['code'], 200)
                self.assertEqual(result.json['bot_message']['msg_content']['qas_response'][0]['question'], low_freq_qas_data[question]['question'])
                self.assertEqual(result.json['bot_message']['msg_content']['qas_response'][0]['answer']['text'], low_freq_qas_data[question]['answer']['text'])

        except BaseException as e:
            info_logger.error("test021_low_freq_message测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            raise BaseException("test021_low_freq_message测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())



    def test030_cnn_message(self):
        try:
            info_logger.info("Start Testing Prediction Message Chat")
            post_body = basic_post_body.copy()
            post_body['user_message'] = {
                "text": "为什么你们就是不通过我的信用卡申请！！！"
            }
            result = self.simulate_post('/chatbot/message', json=post_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['bot_message']['msg_content']['qas_response'][0]['answer']['text'], "您好！申请的结果是我行根据职业、收入、年龄及其它多方面的个人资料审核的一个综合情况。请不要灰心哦，如您个人资料有变更后可再次申请，感谢您对我行支持，谢谢！")

            #开始验证db信息
            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.model_id, self.curr_model_config['model_id'])
            self.assertEqual(latest_msg_record.user_msg, '为什么你们就是不通过我的信用卡申请！！！')
            self.assertEqual(latest_msg_record.user_res_type, 'text')
            self.assertNotEqual(latest_msg_record.ques_cat, '')
            self.assertEqual(latest_msg_record.survey_enabled, self.curr_model_config['survey']['function_enabled'])
            self.assertEqual(latest_msg_record.survey_grade, -1)
            self.assertEqual(latest_msg_record.survey_feedback, '')
            info_logger.info("Complete Testing Prediction Message Chat")
        except BaseException as e:
            info_logger.error("CNN_MESSAG测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            info_logger.error("CNN_MESSAGE 收到的reponse是: " + json.dumps(result.json, ensure_ascii=False))
            info_logger.error("CNN_MESSAGE 后最新的Message是: " + json.dumps(latest_msg_record.user_msg, ensure_ascii=False))
            raise BaseException("CNN_MESSAG测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())

    def test040_survey_good_message_on_qas_match(self):
        try:
            if self.curr_model_config['survey']['function_enabled'] is False:
                info_logger.info("Survey Good Function Testing Skipped, function is not enabled")
                pass
            info_logger.info("Start Survey Good Function Testing")
            post_body = basic_post_body.copy()
            post_body['user_message'] = {
                "text": "为什么你们就是不通过我的信用卡申请！！！"
            }
            msg_result = self.simulate_post('/chatbot/message', json=post_body)
            
            # message id for survey use
            message_id_for_survey = msg_result.json['bot_message']['id']
            # test survey function after client has received survey enabled response
            survey_good_request_body = basic_post_body.copy()
            survey_good_request_body['message_id'] = message_id_for_survey
            survey_good_request_body ['survey_grade'] = 1
            # satisfied
            result = self.simulate_post('/chatbot/survey', json=survey_good_request_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['text'], self.curr_model_config['survey']['good_response'])

            #开始验证db信息
            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.survey_enabled, True)
            self.assertEqual(latest_msg_record.survey_grade, 1)
            self.assertEqual(latest_msg_record.survey_feedback, '')
            info_logger.info("Complete Testing Survey Good Survey Function")
        except BaseException as e:
            info_logger.error(" Good Function Testing测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            raise BaseException(" Good Function Testing测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())

    def test050_survey_bad_message(self):
        try:
            if self.curr_model_config['survey']['function_enabled'] is False:
                info_logger.info("Testing Survey Bad Function Skipped, function is not enabled")
                pass
            info_logger.info("Start Testing Survey Bad Function")
            post_body = basic_post_body.copy()
            post_body['user_message'] = {
                "text": "为什么你们就是不通过我的信用卡申请！！！"
            }
            msg_result = self.simulate_post('/chatbot/message', json=post_body)
            # message id for survey use
            message_id_for_survey = msg_result.json['bot_message']['id']
            # test survey function after client has received survey enabled response
            survey_bad_request_body = basic_post_body.copy()
            survey_bad_request_body['message_id'] = message_id_for_survey
            survey_bad_request_body ['survey_grade'] = 0
            result = self.simulate_post('/chatbot/survey', json=survey_bad_request_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['text'], self.curr_model_config['survey']['bad_response_ask_feedback'])
            self.assertEqual(result.json['survey_codes'], self.curr_model_config['survey']['codes'])

            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.survey_enabled, True)
            self.assertEqual(latest_msg_record.survey_grade, 0)
            self.assertEqual(latest_msg_record.survey_feedback, '')

            survey_feedback_request_body = basic_post_body.copy()
            survey_feedback_request_body['message_id'] = message_id_for_survey
            survey_feedback_request_body["survey_feedback"] = 1
            result = self.simulate_post('/chatbot/survey', json=survey_feedback_request_body)
            self.assertEqual(result.json['status']['code'], 200)
            self.assertEqual(result.json['text'], self.curr_model_config['survey']['bad_response_respond_feedback'])

            latest_msg_record = find_latest_msg_record(test_user_id)
            self.assertEqual(latest_msg_record.survey_enabled, True)
            self.assertEqual(latest_msg_record.survey_grade, 0)
            self.assertEqual(latest_msg_record.survey_feedback, self.curr_model_config['survey']['codes'][0]['text'])

            info_logger.info("Complete Testing Survey Bad Function")
        except BaseException as e:
            info_logger.error(" survey_bad_message测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
            raise BaseException(" Good survey_bad_message测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())       

    # def test060_swap_model(self):
    #     try: 
    #         new_model = list(ModelORM.select().where(ModelORM._id != self.curr_model_config['model_id']).execute())[0]
    #         info_logger.info("Preparing to switch to " + new_model._id + ", start deploying")
    #         swap_model_result = self.simulate_post('/operation/deploy', json={'transaction_id': test_transaction_id, "deploy_model_id":  new_model._id})
    #         self.curr_model_config = json.loads(new_model.config, encoding='utf-8')
    #         self.test010_welcome_message()
    #         self.assertEqual(swap_model_result.json['status']['code'], 200)
    #         info_logger.info("Successfully switched to " + new_model._id + ", start testing")
    #         self.test010_welcome_message()
    #         self.test020_regex_message()
    #         self.test030_cnn_message()
    #         self.test040_survey_good_message_on_qas_match()
    #         self.test050_survey_bad_message()
    #     except BaseException as e:
    #         info_logger.error("Swap_Model测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())
    #         raise BaseException("Swap_Model测试失败, 具体原因: " +str(e) + "\n" + traceback.format_exc())


if __name__ == '__main__':
    unittest.main()
