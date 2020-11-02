import sqlite3


class MyDb(object):
    def __init__(self):
        self.db = sqlite3.connect("./rundb.db")
        self._tableinit()

    def _tableinit(self):
        cursor = self.db.cursor()
        try:
            create_tb_cmd = '''
            CREATE TABLE "app_info" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "appid" text,
                "app_name" text,
                "check" integer
                );
            '''
            # 主要就是上面的语句 : CREATE TABLE IF NOT EXISTS USER
            cursor.execute(create_tb_cmd)
        except Exception:
            # print("Create table failed")
            pass

    def listApps(self, tbl_name: str = 'app_info'):
        cursor = self.db.cursor()
        sql = '''
        SELECT
            *
        FROM
            {0}
                '''.format(tbl_name)
        res = cursor.execute(sql)
        querys = res.fetchall()
        return querys

    def saveItem(self, data: list, tbl_name: str = 'app_info'):
        cursor = self.db.cursor()
        sql = '''
        INSERT INTO {0} ( `appid`, `app_name`, `check` )
        VALUES
            {1}
        '''.format(tbl_name, ','.join(str(i) for i in data))
        cursor.execute(sql)
        self.db.commit()
        return True

    def find(self, key: str, value: str, tbl_name: str = 'app_info'):
        cursor = self.db.cursor()
        sql = '''
        SELECT
            * 
        FROM
            {0}
        WHERE
            {1} = '{2}'
                '''.format(tbl_name, key, value)
        res = cursor.execute(sql)
        querys = res.fetchall()
        return querys

    def delect(self, key: str, value: str, tbl_name: str = 'app_info'):
        cursor = self.db.cursor()
        sql = '''
        DELETE
        FROM
            {0}
        WHERE
            {1} = '{2}'
        '''.format(tbl_name, key, value)
        cursor.execute(sql)
        self.db.commit()
        return True

    def clear(self, tbl_name: str = 'app_info'):
        cursor = self.db.cursor()
        sql = '''
        DELETE
        FROM
            {0}
        '''.format(tbl_name)
        cursor.execute(sql)
        self.db.commit()
        return True

    def runSql(self, sql_str: str):
        cursor = self.db.cursor()
        cursor.execute(sql_str)
        self.db.commit()
        return True
