import urllib.request
import json
import mysql.connector



# Abfrage der externen API.
url = "https://creativecommons.tankerkoenig.de/json/list.php?lat=51.324&lng=7.697&rad=25&sort=dist&type=all&apikey=33e99509-7b2b-c804-469d-45a316652ef6"
response = urllib.request.urlopen(url)
data = json.loads(response.read())

# Überprüfen ob der Anbieter die Daten für in Ordnung hält.
if not data.get('ok'):
    raise SystemExit('error while reeding data!')

connection = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="qGD0zc5iKsvhyjwO",
    database="tankdaten"
)

"""Überprüft ob eine Station existiert."""


def stationExist(stationid, cursor):
    cursor.execute("SELECT id FROM Tankstellen WHERE id='" + stationid + "';")
    if len(cursor.fetchall()) == 1:
        return True
    return False


"""Erstellt eine neue Station."""


def createStation(station, cursor):
    cursor.execute("INSERT INTO Tankstellen (id, name, brand, houseNumber, postCode, place, lat, lng, street)" +
                   "VALUES (" +
                   "'" + station["id"] +
                   "', '" + station["name"] +
                   "', '" + station["brand"] +
                   "', '" + str(station["houseNumber"]) +
                   "', " + str(station["postCode"]) +
                   ", '" + station["place"] +
                   "', " + str(station["lat"]) +
                   ", " + str(station["lng"]) +
                   ", '" + station["street"] + "');")


"""Generiert die Query um Preisdaten der Datenbank hinzuzufügen."""


def getinsertquery(station):
    # Überprüft in der Funktion ob die Preise existieren
    return ("INSERT INTO Preise (id, diesel, e5, e10)" +
            " VALUE (" +
            "'" + station["id"] +
            "', '" + str([station["diesel"], '0'][station["diesel"] is None]) +
            "', '" + str([station["e5"], '0'][station["e5"] is None]) +
            "', '" + str([station["e10"], '0'][station["e10"] is None]) +
            "');")


"""Startet einen Crawl durchlauf."""


def start():
    cursor = connection.cursor()
    try:
        for station in data.get('stations'):
            if not stationExist(stationid=station["id"], cursor=cursor):
                createStation(station, cursor)
            cursor.execute(getinsertquery(station))
        connection.commit()

    except:
        print("Error while fetching data!")


# Für Cronjob start manuell auslösen.
start()
