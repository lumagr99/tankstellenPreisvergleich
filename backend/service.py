import json
from datetime import datetime

from flask import Flask
from flask import request

from backend.database.DatabaseSingleton import DatabaseSingleton

app = Flask(__name__)

# TODO fehlerhafte parameter abfangen

d = ""

d = DatabaseSingleton.getInstance()
print("service")
# app.run()

""" Ermittlung der durchschnittlichen Kraftstoffpreise
mit der URL /preise und den URL-Parametern:
filter=[all/durchschnitt],
begin=[StartZeitpunkt, default 2021-01-15 00:00:00],
end=[endZeitpunkt, default currentTimestamp]
interval=[days/hours/weekdays/hourmin, gibt Monatstage, Stunden, Wochentage oder Stunden:Minuten genaue Preisstatistik, nur bei filter=[all/id]]
id = [id, gibt Preisstatistik für eine ID, nur bei filter=id]"""


@app.route('/preise')
def preise():
    filter = request.args.get('filter', default='all', type=str)

    begin = request.args.get('begin', default="2021-01-16 00:00:00", type=str)
    end = request.args.get('end', default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), type=str)
    interval = request.args.get("interval", "days", str)
    id = request.args.get("id", "0", str)

    # Durchschnittspreise für alle Kraftstoffarten
    if filter == "durchschnitt":
        return json.dumps(durchschnittsWerte(begin, end))
    elif filter == "id":
        return json.dumps(getTankstellenPreis(interval, begin, end, id))
    elif filter == "all":
        return json.dumps(getTankstellenPreis(interval, begin, end))

    return "Anfrage nicht gefunden."


"""Anzeige von Tankstellen mit der URL /tankstellen und den URL-Parametern:
id = [tankstellenID, nur wenn nach ID gefiltert werden soll!"""


@app.route('/tankstellen')
def tankstellen():
    t_id = request.args.get('id', default="0", type=str)

    query = "select id, name, place, street, housenumber, lat, lng from Tankstellen %s;"
    if t_id != "0":
        query = query.replace("%s", "where id = '" + t_id + "'")
    else:
        query = query.replace("%s", "")

    cursor = d.getCursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    ret = {}
    for c in data:
        if c[0] not in ret:
            ret[c[0]] = {
                "name": c[1],
                "place": c[2],
                "street": c[3],
                "number": c[4],
                "coord": {
                    "lat": str(c[5]),
                    "lng": str(c[6])
                }
            }
    return ret

    # Zeigt eine Tankstelle an
    # Benötigter Parameter: id = [tankstellenID, default 0]


"""ONLY id, name, place, stress, housenumber"""


def sqlToJSONTankstelle(result):
    data = []

    for res in result:
        x = {
            "id": res[0],
            "name": res[1],
            "place": res[2],
            "street": res[3],
            "housenumber": res[4]
        }
        data.append(x)

    return json.dumps(data)


"""Ermittelt eine Liste von Preisen, orientiert an Stunden [hours], Wochentagen [weekdays] oder Monatstagen [days], 
nach IDs aufgeteilt oder nicht.
Stunden [hours],  Tage [days], Wochentage [weekdays] oder Stunden:Minuten [hourmin] können angegeben werden.
begin und end für den aktuellen Tag nicht angeben, ansonsten den Tag mit Stunden angeben.
id angeben um nach der id zu filtern"""


def getTankstellenPreis(interval="days", begin=datetime.now().strftime("%Y-%m-%d 00:00:00"),
                        end=datetime.now().strftime("%Y-%m-%d 23:23:59"), id=""):
    query = ""

    avg = durchschnittsWerte(begin, end)
    if interval == "days" or interval == "weekdays":
        query = "SELECT id, round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel , timedate, " + \
                "avg(e5/" + str(avg['e5']) + ") as 'e5Faktor', " + \
                "avg(e10/" + str(avg['e10']) + ") as 'e10Faktor', " + \
                "avg(diesel/" + str(avg['diesel']) + ") as 'dieselFaktor' FROM `Preise` " + \
                "where %id timedate between '" + str(begin) + "' and '" + str(end) + "' " + \
                "group by id, cast(timedate As Date)"
    elif interval == "hours":
        query = "SELECT id, round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel, HOUR(timedate) as hours, " + \
                "avg(e5/" + str(avg['e5']) + ") as 'e5Faktor', " + \
                "avg(e10/" + str(avg['e10']) + ") as 'e10Faktor', " + \
                "avg(diesel/" + str(avg['diesel']) + ") as 'dieselFaktor' FROM `Preise` " + \
                "where %id timedate between '" + begin + "' and '" + end + "' " + \
                "group by HOUR(timedate)"
    elif interval == "hourmin":
        query = "SELECT id, round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel, CONCAT(HOUR(timedate), ':',MINUTE(timedate)) as hours, " + \
                "avg(e5/" + str(avg['e5']) + ") as 'e5Faktor', " + \
                "avg(e10/" + str(avg['e10']) + ") as 'e10Faktor', " + \
                "avg(diesel/" + str(avg['diesel']) + ") as 'dieselFaktor' FROM `Preise` " + \
                "where %id timedate between '" + begin + "' and '" + end + "' " + \
                "group by hours, id;"

    if id == "":
        query = query.replace("%id", "")
    else:
        query = query.replace("%id", " id='" + id + "' and")

    cursor = d.getCursor()
    cursor.execute(query)

    res = cursor.fetchall()

    ret = {}
    for r in res:
        x = r[4]
        if interval == "days":
            x = x.replace(second=0, minute=0, hour=0)
        elif interval == "weekdays":
            x = ("monday", "tuesday", "thursday", "wednesday", "friday", "saturday", "sunday")[x.weekday()]
        x = str(x)
        if x not in ret:
            ret[x] = {}

        e5 = r[1]
        e10 = r[2]
        diesel = r[3]
        if not r[0] == "AVG":
            e5 = {
                "price": r[1],
                "factor": r[5]
            }
            e10 = {
                "price": r[2],
                "factor": r[6]
            }
            diesel = {
                "price": r[3],
                "factor": r[7]
            }

        ret[x][r[0]] = {
            "e5": e5,
            "e10": e10,
            "diesel": diesel
        }

    query = "SELECT round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel, " + \
            "CONCAT(HOUR(timedate), ':',MINUTE(timedate)) as hours FROM `Preise` where timedate between '" + begin + \
            "' and '" + end + "' group by hours;"
    cursor.execute(query)
    res = cursor.fetchall()
    cursor.close()

    for r in res:
        x = r[3]
        ret[x]["AVG"] = {
            "e5": r[0],
            "e10": r[1],
            "diesel": r[2]
        }

    return ret


"""Berechnet den Durchschnittswert der Kraftstoffpreise zwischen zwei Zeitpunkten."""


def durchschnittsWerte(begin, end):
    cursor = d.getCursor()
    cursor.execute \
        ("select avg(e10), avg(e5), avg(diesel) from Preise where "
         "timedate BETWEEN '" + begin + "' "
                                        "AND '" + end + "' AND e5 <> 0 AND e10 <> 0 AND diesel <> 0")
    result = cursor.fetchall()
    ret = {'e10': result[0][0], 'e5': result[0][1], 'diesel': result[0][2],
           'time': {'begin': begin, 'end': end}}
    return ret


if __name__ == '__main__':
    app.run()

# install flask