import urllib
import json

import mysql.connector
from flask import Blueprint, render_template, session, request, redirect, url_for

page = Blueprint('tankstellenliste', __name__, template_folder='templates')

backend_url_prefix = "http://127.0.0.1:5000"

db = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="qGD0zc5iKsvhyjwO",
    database="tankdaten"
)


"""Zeigt eine Übersicht über alle Tankstellen.
Ermöglicht das zuordnen von Favoriten."""
@page.route('/tankstellen', methods=['GET', 'POST'])
def show():
    if request.method == 'GET':
        usertankstellen = []
        url = backend_url_prefix + "/tankstellen"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen

        id = ""
        if 'loggedin' in session:
            id = session.get('id')
            cursor = db.cursor()
            cursor.execute('SELECT tankstellenid FROM Benutzer2Tankstelle where BenutzerID = %s;', (id,))
            for curr in cursor.fetchall():
                usertankstellen.append(curr[0])
            cursor.close()
        db.commit()

        tankstellen_list = []
        for t in data:
            tankstellen_list.append(
                [data[t]["name"] + "-" + data[t]["place"], t])  # Alle Tankstellen in einer Liste speichern

        return render_template('tankstellen.html', tankstellen=tankstellen_list, usertankstellen=usertankstellen)
    if request.method == 'POST':
        if 'loggedin' in session:
            id = session.get('id')

            cursor = db.cursor()
            # Alle Zuordnungen entfernen, anschließend neu zuordnen.
            cursor.execute(
                'DELETE FROM Benutzer2Tankstelle WHERE benutzerID = %s',
                (id,))
            for item in request.form:
                if request.form[item] == 'on':
                    cursor.execute('INSERT INTO Benutzer2Tankstelle(BenutzerID, TankstellenID) VALUES (%s, %s)',
                                   (id, item[:-9],))
            cursor.close()
            db.commit()
            return redirect(url_for('tankstellenliste.show'))
    return "Ein Fehler ist aufgetreten."


@page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
def tankstelle(tankstelle_id):
    return "Coming soon!"
