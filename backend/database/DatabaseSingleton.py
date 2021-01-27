import mysql.connector


class DatabaseSingleton:
    __instance__ = None
    __connection__ = ""

    def __init__(self):
        if DatabaseSingleton.__instance__ is None:
            DatabaseSingleton.__instance__ = self
            self.__connection__ = mysql.connector.connect(
                host="45.88.109.79",
                user="tankstellenCrawler",
                password="qGD0zc5iKsvhyjwO",
                database="tankdaten"
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
