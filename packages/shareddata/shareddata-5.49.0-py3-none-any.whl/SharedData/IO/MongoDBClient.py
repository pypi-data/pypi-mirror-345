import os

from pymongo import MongoClient, errors
from pymongo import ASCENDING, DESCENDING

class MongoDBClient:
    _instance = None
    _user = None

    def __new__(cls, user=None):
        if cls._user is None:
            cls._user = user

        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            mongodb_conn_str = (f'mongodb://{os.environ["MONGODB_USER"]}:'
                                f'{os.environ["MONGODB_PWD"]}@'
                                f'{os.environ["MONGODB_HOST"]}:'
                                f'{os.environ["MONGODB_PORT"]}/')
            cls._instance.client = MongoClient(mongodb_conn_str)
        return cls._instance

    def __getitem__(self, collection_name):
        if self._user is None:
            return self._client['SharedData'][collection_name]
        else:
            return self._client[self._user][collection_name]

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value    