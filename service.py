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
# filter=all,
# begin=[StartZeitpunkt, default 15-01-2020 00:00:00],
# end=[endZeitpunkt, default currentTimestamp]
@app.route('/preise')
def preise():
    filter = request.args.get('filter', default='all', type=str)
    cursor = connection.cursor()

    # Für alle Kraftstoffarten
    if filter == "all":
        begin = request.args.get('begin', default="15-01-2021 00:00:00", type=str)
        end = request.args.get('end', default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), type=str)
        cursor.execute\
            ("select avg(e10), avg(e5), avg(diesel) from Preise where "
             "timedate BETWEEN '" + begin + "' "
             "AND '" + end + "' AND e5 <> 0 AND e10 <> 0 AND diesel <> 0")
        result = cursor.fetchall()
        print(result)
        ret = {'e10' : result[0][0], 'e5' : result[0][1], 'diesel' : result[0][2],
               'time' : {'begin' : begin, 'end' : end}}
        return ret

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
        #x = (res[0], res[1], res[2], res[3], res[4])
        x = {
            "id": res[0],
            "name": res[1],
            "place": res[2],
            "street": res[3],
            "housenumber": res[4]
        }
        data.append(x)

    return json.dumps(data)


if __name__ == '__main__':
    app.run()

# install flask
