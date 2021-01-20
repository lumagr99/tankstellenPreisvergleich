from flask import Flask
from flask import request
import mysql.connector
import json
from datetime import datetime

app = Flask(__name__)

# TODO fehlerhafte parameter abfangen

connection = mysql.connector.connect(
    host="localhost",
    user="tankstellenData",
    password="tankstellenData2021",
    database="tankstellenData"
)


# Ermittlung der durchschnittlichen Kraftstoffpreise
# mit der URL /preise und den URL-Parametern:
# filter=[all/durchschnitt/time],
# begin=[StartZeitpunkt, default 15-01-2020 00:00:00, nur bei all, time],
# end=[endZeitpunkt, default currentTimestamp, nur bei all, time]
# amount=[Anzahl der zurückzugebenden Werte, default 200, nur bei durchschnitt]
# groupById =[True/False, Gruppiert nach der id oder nur nach der Zeit, nur bei time]
@app.route('/preise')
def preise():
    filter = request.args.get('filter', default='all', type=str)

    begin = request.args.get('begin', default="2021-01-16 00:00:00", type=str)
    end = request.args.get('end', default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), type=str)

    # Durchschnittspreise für alle Kraftstoffarten
    if filter == "durchschnitt":
        return json.dumps(durchschnittsWerte(begin, end))
    elif filter == "all":
        # URL Parameter basis gibt an, ob der geringste [min], größte [max] oder durchschnittswert [avg]
        # einer Tankstelle zurückgegeben werden soll.
        basis = request.args.get('basis', default="min", type=str)

        # URL Parameter order gibt an, ob nach e5Faktor, e10Faktor oder dieselFaktor sortiert werden soll.
        order = request.args.get('order', default="e5Faktor", type=str)

        avg = durchschnittsWerte(begin, end)
        query = "select id, [BASIS](e5), avg(e5/" + str(avg['e5']) + ") as 'e5Faktor', [BASIS](e10), avg(e10/" + \
                str(avg['e10']) + ") as 'e10Faktor', [BASIS](diesel), avg(diesel/" + \
                str(avg['diesel']) + ") as 'dieselFaktor', timedate from Preise where timedate BETWEEN'" \
                + begin + "' and '" + end + "' group by id order by [ORDER]"

        # Basis setzen
        query = query.replace("[BASIS]", basis)

        # Order setzen
        query = query.replace("[ORDER]", order)

        cursor = connection.cursor()
        cursor.execute(query)
        temp = cursor.fetchall()
        ret = []
        for current in temp:
            e5 = {
                "preis": current[1],
                "faktor": current[2]
            }
            e10 = {
                "preis": current[3],
                "faktor": current[4]
            }
            diesel = {
                "preis": current[5],
                "faktor": current[6]
            }
            x = {
                "id": current[0],
                "e5": e5,
                "e10": e10,
                "diesel": diesel,
                "time": str(current[7])
            }
            ret.append(x)
        return json.dumps(ret)

    elif filter == "time":
        interval = request.args.get("interval", "days", str)
        groupbyid = request.args.get("groupbyid", "True", str)
        print(groupbyid)
        return json.dumps(getTankstellenPreis(interval, begin, end, groupbyid))

    return "Anfrage nicht gefunden."


# Anzeige von Tankstellen mit der URL /tankstellen und den URL-Parametern:
# filter = [all/id, default all]
# id = [tankstellenID, nur bei filter=id
@app.route('/tankstellen')
def tankstellen():
    filter = request.args.get('filter', default="all", type=str)
    cursor = connection.cursor()

    # Zeigt alle Tankstellen an
    if filter == "all":
        cursor.execute("select id, name, place, street, housenumber from Tankstellen;")
        return sqlToJSONTankstelle(cursor.fetchall())

    # Zeigt eine Tankstelle an
    # Benötigter Parameter: id = [tankstellenID, default 0]
    if filter == "id":
        t_id = request.args.get('id', default="0", type=str)
        if t_id == "0":
            return "No ID!"
        else:
            cursor.execute("select id, name, place, street, housenumber from Tankstellen where id = '" + t_id + "';")
            return sqlToJSONTankstelle(cursor.fetchall())

    return "Anfrage nicht gefunden."


# ONLY id, name, place, stress, housenumber
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


#TODO Wochentagen

#TODO vereinfachen, Nach Datum bzw. Uhrzeit und darunter: avg, dann die Tankstellen und darunter jeweils die Preise

# Ermittelt eine Liste von Preisen, orientiert an Stunden oder Monatstagen, nach IDs aufgeteilt oder nicht.
# Stunden [hours] oder Tage [days] können angegeben werden.
# begin und end für den aktuellen Tag nicht angeben, ansonsten den Tag mit Stunden angeben.
def getTankstellenPreis(interval="days", begin=datetime.now().strftime("%Y-%m-%d 00:00:00"),
                        end=datetime.now().strftime("%Y-%m-%d 23:23:59"), groupyById="True"):
    query = ""

    if interval == "days":
        query = "SELECT id, round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel , timedate FROM `Preise` " + \
                "where timedate between '" + str(begin) + "' and '" + str(end) + "' " + \
                "group by id, cast(timedate As Date)"
    elif interval == "hours":
        query = "SELECT id, round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel, HOUR(timedate) as hours  FROM `Preise` " + \
                "where timedate between '" + begin + "' and '" + end + "' " + \
                "group by HOUR(timedate)"

    if groupyById == "True":
        query = query + ", id;"

    print(query)
    cursor = connection.cursor()
    cursor.execute(query)

    res = cursor.fetchall()
    ret = {}
    for r in res:
        if groupyById == "True":
            if r[0] not in res:
                ret[r[0]] = []
            ret[r[0]].append({
                "e5": r[1],
                "e10": r[2],
                "diesel": r[3],
                "time": str(r[4])
            })
        else:
            x = r[4]
            if interval == "days":
                x = r[4].replace(second=0, minute=0, hour=0)

            if str(x) not in res:
                ret[str(x)] = []
                ret[str(x)].append({
                    "e5": r[1],
                    "e10": r[2],
                    "diesel": r[3]
                })
    return ret


# Berechnet den Durchschnittswert der Kraftstoffpreise zwischen zwei Zeitpunkten.
def durchschnittsWerte(begin, end):
    cursor = connection.cursor()
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
