# Created by Helic on 2018/7/30
from peewee import *
from database.orm.base_orm import BaseModel


class SmartTopicAnalyser(BaseModel):
    id = CharField(primary_key=True, max_length=128, null=False, column_name='id')
    matched_sentences = CharField(max_length=10000, null=False)
    prob = FloatField(null=False, default=0.7)
    target = CharField(max_length=20, null=False)
    analyser_type = CharField(max_length=45, null=False)

    class Meta:
        table_name = 'smart_topic_analyser'

