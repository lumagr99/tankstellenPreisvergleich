import urllib.request, json
import mysql.connector
import time

url = "https://creativecommons.tankerkoenig.de/json/list.php?lat=51.324&lng=7.697&rad=25&sort=dist&type=all&apikey=33e99509-7b2b-c804-469d-45a316652ef6"
response = urllib.request.urlopen(url)
data = json.loads(response.read())

if not data.get('ok'):
    raise SystemExit('error while reeding data!')

connection = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="kzuANqgSA3CsTOPr",
    database="tankstellenCrawler"
)


def stationExist(stationID, cursor):
    cursor.execute("select id from Tankstellen where id='" + stationID + "';")
    if len(cursor.fetchall()) == 1:
        return True
    return False


def createStation(station, cursor):
    cursor.execute("insert into Tankstellen (id, name, brand, houseNumber, postCode, place, lat, lng, street)" +
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


def insertData(station, cursor):
    print("insert into Preise (id, diesel, e5, e10)" +
                   "values (" +
                   "'" + station["id"] +
                   "', '" + str([station["diesel"], '0'][station["diesel"] is None]) +
                   "', '" + str([station["e5"], '0'][station["e5"] is None]) +
                   "', '" + str([station["e10"], '0'][station["e10"] is None]) +
                   "');")


def start():
    for station in data.get('stations'):
        print(station["id"], station["e5"])
        try:
            cursor = connection.cursor()
            if not stationExist(stationID=station["id"], cursor=cursor):
                pass
                createStation(station, cursor)
            insertData(station, cursor)
            #connection.commit()
        except:
            print("Error while fetching data!")


# Für Cronjob start manuell auslösen.
def startRepeat():
    while True:
        start()
        time.sleep(300)


startRepeat()

# python 3
# mit modulen
# import urllib.request, json
# import mysql.connector
# import time

# sql benutzer mit passenden lesen, schreibe berechtigungen

# das skript muss nach jedem system neustart einmalig neu gestartet werden
