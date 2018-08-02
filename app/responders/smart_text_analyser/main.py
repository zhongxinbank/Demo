# Created by Helic on 2018/7/30
import json
from .smart_text_analyser import SmartTextAnalyser


def run(config_path, dialogs):
    """"""
    with open(config_path, 'r', encoding="utf-8") as f:
        config = json.load(f)
        results = {
            "SmartTextAnalyser": {},
            "RegexTextAnalyser": {},
            "TopicAnalyser": {},
            "EmotionAnalyser": {}
        }

        analyser_ids = config["SmartTextAnalyser"]  # TODO 添加后续analyser
        for analyser_id in analyser_ids:
            smart_analyser = SmartTextAnalyser.load(analyser_id=analyser_id)
            results["SmartTextAnalyser"][analyser_id] = smart_analyser.test(dialogs=dialogs)

        return results


if __name__ == '__main__':
    dialogs = {"1": [("user", "time", "你摸着自己良心我有说错吗？"), ("customer_service", "time", "你是变态啊")],
               "2": [("user", "time", "就你这种人，送给我我都不要"), ("customer_service", "time", "你是变态啊")]}
    print(run(config_path="data/config.json", dialogs=dialogs))
