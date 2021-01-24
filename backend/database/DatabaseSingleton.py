import mysql.connector


class DatabaseSingleton:
    __instance__ = None
    __connection__ = ""

    def __init__(self, dataURL):
        if DatabaseSingleton.__instance__ is None:
            DatabaseSingleton.__instance__ = self
            self.__connection__ = mysql.connector.connect(
                host=dataURL,
                user="tankstellenData",
                password="tankstellenData2021",
                database="tankstellenData"
            )
        else:
            raise Exception("Du kannst keine weitere Instanz erzeugen!")

    @staticmethod
    def getInstance():
        if not DatabaseSingleton.__instance__:
            DatabaseSingleton()
        return DatabaseSingleton.__instance__

    def getCursor(self):
        return self.__connection__.cursor()
