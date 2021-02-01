import urllib
import json

import mysql.connector
from flask import Blueprint, render_template, session

page = Blueprint('tankstellenliste', __name__, template_folder='templates')

backend_url_prefix = "http://127.0.0.1:5000"

db = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="qGD0zc5iKsvhyjwO",
    database="tankdaten"
)


@page.route('/tankstellen', methods=['GET', 'POST'])
def show():
    usertankstellen = []
    url = backend_url_prefix + "/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen

    if 'loggedin' in session:
        id = session.get('id')
        cursor = db.cursor()
        cursor.execute('SELECT tankstellenid FROM Benutzer2Tankstelle where BenutzerID = %s;', (id,))
        usertankstellen = cursor.fetchall()[0]
        cursor.close()
        print(usertankstellen)
    db.commit()

    tankstellen_list = []
    for t in data:
        tankstellen_list.append(
            [data[t]["name"] + "-" + data[t]["place"], t])  # Alle Tankstellen in einer Liste speichern


    return render_template('tankstellen.html', tankstellen=tankstellen_list, usertankstellen=usertankstellen)


@page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
def tankstelle(tankstelle_id):
    return "Coming soon."
