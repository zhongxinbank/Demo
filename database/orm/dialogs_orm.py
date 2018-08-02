from peewee import *
import datetime
from database.orm.base_orm import BaseModel


class Dialogs(BaseModel):

    call_id = CharField(primary_key=True, max_length=128, null=False, column_name='call_id')
    user_id = CharField(max_length=128, null=False)
    content = CharField(max_length=300, null=False)
    time = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        table_name = 'dialogs'
