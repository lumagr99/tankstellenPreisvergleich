from flask import Flask
from flask import request
import mysql.connector
import json
from datetime import datetime

app = Flask(__name__)

connection = mysql.connector.connect(
    host="192.168.178.54",
    user="tankstellenData",
    password="tankstellenData2021",
    database="tankstellenData"
)


# Ermittlung der durchschnittlichen Kraftstoffpreise
# mit der URL /preise und den URL-Parametern:
# filter=[all/durchschnitt],
# begin=[StartZeitpunkt, default 15-01-2020 00:00:00],
# end=[endZeitpunkt, default currentTimestamp]
# amount=[Anzahl der zurückzugebenden Werte, default 200, nur bei durchschnitt]
@app.route('/preise')
def preise():
    filter = request.args.get('filter', default='all', type=str)

    begin = request.args.get('begin', default="2021-01-16 00:00:00", type=str)
    end = request.args.get('end', default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), type=str)

    # Durchschnittspreise für alle Kraftstoffarten
    if filter == "durchschnitt":
        return json.dumps(durchschnittsWerte(begin, end))
    if filter == "all":
        avg = durchschnittsWerte(begin, end)

        # TODO default count = count* from tankstellen
        amount = request.args.get('amount', default=200, type=str)

        #TODO faktoren mit 0 aussortieren
        cursor = connection.cursor()
        cursor.execute("select id, "
                       "avg(e5), avg(e5/" + str(avg['e5']) + ") as 'e5Faktor', "
                                                     "avg(e10), avg(e10/" + str(avg['e10']) + ") as 'e10Faktor', "
                                                                                      "avg(diesel), avg(diesel/" + str(
            avg['diesel']) + ") as 'dieselFaktor', "
                             "timedate from Preise "
                             "where timedate BETWEEN'" + begin + "' and '" + end + "' group by id "
                                                                                   "order by timedate DESC, e5Faktor limit " + str(amount) + "")
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
