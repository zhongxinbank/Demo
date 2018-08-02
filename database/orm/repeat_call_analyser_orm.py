# Created by Helic on 2018/7/30
from peewee import *
from database.orm.base_orm import BaseModel


class RepeatCallAnalyser(BaseModel):
    id = CharField(primary_key=True, max_length=128, null=False, column_name='id')
    matched_sentences = CharField(max_length=10000, null=False)
    prob = FloatField(null=False, default=0.7)
    analyser_type = CharField(max_length=45, null=False, default="重复来电")
    description = CharField(max_length=1024, null=False, default='重复来电')
    time_interval = IntegerField(null=False, default=6)
    logic = CharField(max_length=10, null=False, default='and')

    class Meta:
        table_name = 'repeat_call_analyser'




