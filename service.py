from flask import Flask
from flask import request
import mysql.connector
import json

app = Flask(__name__)

connection = mysql.connector.connect(
    host="192.168.178.54",
    user="tankstellenData",
    password="tankstellenData2021",
    database="tankstellenData"
)

#TODO SQL to JSON dump with parameter names

@app.route('/tankstellen')
def tankstellen():
    filter = request.args.get('filter', default="all", type=str)

    cursor = connection.cursor()
    if filter == "all":
        cursor.execute("select id, name, place, street, housenumber from Tankstellen;")
        return json.dumps(cursor.fetchall())

    if filter == "id":
        t_id = request.args.get('id', default="0", type=str)
        if t_id == "0":
            return "No ID!"
        else:
            cursor.execute("select id, name, place, street, housenumber from Tankstellen where id = '" + t_id + "';")
            return json.dumps(cursor.fetchall())

    return 'Hello, World!' + filter


if __name__ == '__main__':
    app.run()

#install flask