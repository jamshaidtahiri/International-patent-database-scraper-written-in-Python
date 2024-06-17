#db.py
from mongoengine import (
    Document,
    connect,
    StringField,
    DateField,
    ListField,
    FloatField,
    DictField,
    DateTimeField,
    IntField,
)
import datetime
import os

# MongoDB Setup
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/patents')
connect(host=MONGO_URI)

class MongoPatent(Document):
    patent_number = StringField(unique=True, required=True)
    applicants = ListField(StringField())
    title = StringField()
    publication_number = StringField()
    application_number = StringField()
    publication_date = DateField()
    application_date = DateField()
    abstract = StringField()
    inventors = ListField(StringField())
