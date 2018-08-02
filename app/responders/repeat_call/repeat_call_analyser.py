import re
from app.responders.repeat_call.tfidfTestSklearn import Tfidf
from .utils import *


class RepeatCallAnalyser:
    def __init__(self, analyser_id, matched_sentences, prob, analyser_type, description, time_interval, logic):
        """"""
        self.analyser_id = analyser_id
        self.matched_sentences = matched_sentences  # list
        self.prob = prob
        self.analyser_type = analyser_type
        self.description = description
        self.time_interval = time_interval
        self.logic = logic

    @classmethod
    def load(cls, analyser_id, matched_sentences, prob, analyser_type, description, time_interval, logic):
        """返回一个RepeatCallAnalyser instance"""
        matched_sentences = list(map(lambda x: x.strip(), matched_sentences.split('\n')))
        return cls(analyser_id, matched_sentences, prob, analyser_type, description, time_interval, logic)

    def create_model(self, input_dic):
        """建立新的重复来电检测模型，存入json中
        输入: {"action”:”add_expression”, "item”:{"logic_expression”:[], "time_interval”:  " ”,
                                                 "logic_relationship”: " ”}}
        输出：{”status”:"True/False” , "location”:”   ”}
        """
        # 判断json文件中是否已存在相同的模型
        model = load_model(self.model_path)
        same_model = set(input_dic["item"]["logic_expression"]) & set(model["logic_expression"])
        if same_model:
            return {"status": "False", "location": os.path.join(self.model_path),
                    "message": "the input model {} already exsits".format(list(same_model))}
        else:
            model["time_interval"] = input_dic["item"]["time_interval"]
            model["logic_relationship"] = input_dic["item"]["logic_relationship"]
            model["logic_expression"].extend(input_dic["item"]["logic_expression"])
            flag = write_model(self.model_path, model)
            if flag:
                return {"status": "True", "location": os.path.join(self.model_path)}
            else:
                return {"status": "False", "location": os.path.join(self.model_path)}

    def edit_model(self, input_dic):
        """修改模型
        :param input_dic:{"action”:”edit_expression”, "item”:{"logic_expression”:{old:new}, "time_interval”:  " ”,
                                                 "logic_relationship”: " ”}}
        :return {”status”:"True/False” , "location”:”   ”}"""
        model = load_model(self.model_path)
        model["time_interval"] = input_dic["item"]["time_interval"]
        model["logic_relationship"] = input_dic["item"]["logic_relationship"]
        for key in input_dic["item"]["logic_expression"]:
            model["logic_expression"].remove(key)
            model["logic_expression"].append(input_dic["item"]["logic_expression"][key])
        flag = write_model(self.model_path, model)
        if flag:
            return {"status": "True", "location": os.path.join(self.model_path)}
        else:
            return {"status": "False", "location": os.path.join(self.model_path)}

    def delete_model(self, input_dic):
        """删除重复来电检测模型，存入json中
        :param input_dic: {"action”:”delete_expression”, "item”:{"logic_expression”:[]}}
        :return: {”status”:"True/False” , "location”:”   ”}
        """
        model = load_model(self.model_path)
        if set(input_dic["item"]["logic_expression"]) <= set(model["logic_expression"]):
            for i in input_dic["item"]["logic_expression"]:
                model["logic_expression"].remove(i)
            write_model(self.model_path, model)
            flag = write_model(self.model_path, model)
            if flag:
                return {"status": "True", "location": os.path.join(self.model_path)}
            else:
                return {"status": "False", "location": os.path.join(self.model_path)}
        else:
            return {"status": "False", "location": os.path.join(self.model_path), "message": "the model did not exist"}

    def test(self, dialogs):
        """
        针对于单个analyser做测试
        :param dialogs: {"call_id": {"content":[("user", "start_time", "end_time", "你摸着自己良心我有说错吗？"),
                                          ("customer_service", "start_time", "end_time", "你是变态啊")],
                                     "user_id": ""
                                     "time": datetime}
                        }
        :return  result: {
                            "0": {
                                "status": true,
                                "source": "all"
                                "matched": [
                                    ["source_sentence", "matched_sentence", similarity]
                                ],
                                "time_interval": 6
                            },
                            "1": {
                                "status": false,
                                "source": "all"
                                "matched": [],
                                "time_interval": 6
                            }
                        }
        """
        tfidf = Tfidf()
        results = {}

        for dialog_id in dialogs:
            logic_flag, time_flag = False, False
            results[dialog_id] = {"status": None, "source": "", "matched": [], "time_interval": 6}
            # 测试时间间隔
            user_id = dialogs[dialog_id]["user_id"]
            time = dialogs[dialog_id]["time"]
            time_list = list(
                map(lambda x: dialogs[x]["time"] if dialogs[x]["user_id"] == user_id and x != dialog_id else "",
                    dialogs))
            time_interval = min(map(lambda x: get_interval_time(x, time) if x != "" else 10000, time_list))
            if time_interval <= self.time_interval:
                time_flag = True
                results[dialog_id]["time_interval"] = time_interval
            else:
                results[dialog_id]["time_interval"] = 10000

            # 测试句子相似度
            dialog = dialogs[dialog_id]["content"]
            for sentence in dialog:
                matched = tfidf.main(sentence[-1], self.matched_sentences, value=self.prob)
                if matched:
                    matched = list(matched)
                    matched.insert(0, sentence[-1])
                    results[dialog_id]["matched"].append(matched)
                    logic_flag = True

            if logic_flag and time_flag:
                results[dialog_id]["source"] = "both"
            elif logic_flag and (not time_flag):
                results[dialog_id]["source"] = "similarity"
            elif (not logic_flag) and time_flag:
                results[dialog_id]["source"] = "time_interval"

            if self.logic == "and":
                results[dialog_id]["status"] = True if results[dialog_id]["source"] == "both" else False
            else:
                results[dialog_id]["status"] = True if results[dialog_id]["source"] != "" else False

        return results
