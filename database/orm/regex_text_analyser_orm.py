# Created by Helic on 2018/8/1
from peewee import *
from database.orm.base_orm import BaseModel


class RegexTextAnalyser(BaseModel):
    id = CharField(primary_key=True, max_length=128, null=False, column_name='id')
    keywords = CharField(max_length=1024, null=False)
    target = CharField(max_length=20, null=False, default='all')
    logic = CharField(max_length=10, null=False, default='or')
    analyser_type = CharField(max_length=45, null=False)

    class Meta:
        table_name = 'regex_text_analyser'

