import psycopg2


class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.init_db_connection(*args, **kwargs)
        return cls._instance

    def init_db_connection(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

