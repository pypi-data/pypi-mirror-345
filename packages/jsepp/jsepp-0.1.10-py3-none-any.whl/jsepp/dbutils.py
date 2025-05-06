import pymysql
import pymongo
import urllib


class MySQLConn(object):
    def __init__(self, host: str, user: str, password: str, db: str, port: int):
        self.conn = pymysql.connect(host=host, user=user, password=password, db=db, port=port)
        self.cursor = self.conn.cursor()
        self.dict_cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def excute_one(self, comm, dict=False):
        if dict:
            self.dict_cursor.execute(comm)
            res = self.dict_cursor.fetchone()
        else:
            self.cursor.execute(comm)
            res = self.cursor.fetchone()
        if res is None:
            return None
        elif len(res) == 1:
            return res[0]
        else:
            return res

    def excute_all(self, comm, dict=False):
        if dict:
            self.dict_cursor.execute(comm)
            return self.dict_cursor.fetchall()
        else:
            self.cursor.execute(comm)
            return self.cursor.fetchall()

    def insert_confirm(self, comm):
        x = self.cursor.execute(comm)
        if x > 0:
            self.conn.commit()
        else:
            self.conn.rollback()
        return x

    def insert(self, comm):
        return self.cursor.execute(comm)

    def confirm(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()


class MongoConn(object):
    def __init__(self, user:str, password:str, host:str, port:int, db:str, authMechanism:str='DEFAULT', authSource:str=None):
        if authSource is None:
            self.conn = pymongo.MongoClient(f'mongodb://{urllib.parse.quote_plus(user)}:{urllib.parse.quote_plus(password)}@{host}:{port}'
                                            f'/?authMechanism={authMechanism}')
        else:
            self.conn = pymongo.MongoClient(f'mongodb://{urllib.parse.quote_plus(user)}:{urllib.parse.quote_plus(password)}@{host}:{port}'
                                            f'/?authMechanism={authMechanism}&authSource={authSource}')
        self.cursor = self.conn[db]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def fetch_one(self, tablename:str, filter: dict):
        return self.cursor[tablename].find_one(filter)

    def update_one(self, tablename:str, filter:dict, data:dict):
        x = self.fetch_one(tablename, filter)
        if x:
            return self.cursor[tablename].update_one(filter, {'$set': data})
        else:
            return None

    def insert_one(self, tablename:str, data:dict):
        self.cursor[tablename].insert_one(data)


