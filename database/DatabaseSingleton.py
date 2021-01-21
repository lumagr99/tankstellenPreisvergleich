import mysql.connector


class DatabaseSingleton:
    __instance__ = None
    __connection__ = mysql.connector.connect(
        host="192.168.178.54",
        user="tankstellenData",
        password="tankstellenData2021",
        database="tankstellenData"
    )

    def __init__(self):
        if DatabaseSingleton.__instance__ is None:
            DatabaseSingleton.__instance__ = self
        else:
            raise Exception("Du kannst keine weitere Instanz erzeugen!")

    @staticmethod
    def getInstance():
        if not DatabaseSingleton.__instance__:
            DatabaseSingleton()
        return DatabaseSingleton.__instance__

    def getCursor(self):
        return self.__connection__.cursor()
