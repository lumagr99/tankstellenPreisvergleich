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
    database="tankdaten",
    autocommit=True
)

"""Zeigt eine Übersicht über alle Tankstellen.
Ermöglicht das zuordnen von Favoriten."""


@page.route('/tankstellen', methods=['GET', 'POST'])
def show():
    if request.method == 'GET':
        url = backend_url_prefix + "/tankstellen"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen

        id = "-1"
        if 'loggedin' in session:
            id = session.get('id')
        return show_tankstellen(id, data, get_favorites(id), "tankstellenliste.show")

    if request.method == 'POST':
        if 'loggedin' in session:
            update_favorites(session.get('id'), request.form)  # Aktualisierungen verarbeiten.
            return redirect(url_for('tankstellenliste.show'))
    return "Ein Fehler ist aufgetreten."


"""Generiert eine Favoritenliste."""


@page.route('/favoriten', methods=['GET', 'POST'])
def favorites():
    if request.method == 'GET':
        id = "-1"
        if 'loggedin' in session:
            id = session.get('id')

            url = backend_url_prefix + "/tankstellen"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen
            favoriten = {}  # Liste von Tankstellenobjekten
            favoriten_ids = get_favorites(id)  # Liste von IDs
            for t in data:  # IDs in Tankstellenobjekte umwandeln
                if t in favoriten_ids:
                    favoriten[t] = data[t]

            return show_tankstellen(id, favoriten, favoriten_ids, "tankstellenliste.favorites")

    if request.method == 'POST':
        if 'loggedin' in session:
            update_favorites(session.get('id'), request.form)  # Aktualisierungen verarbeiten.
            return redirect(url_for('tankstellenliste.favorites'))
    return redirect(url_for('tankstellenliste.show'))


"""Übergibt die notwendigen Daten."""


def show_tankstellen(id, tankstellen, favorites, action):
    tankstellen_list = []
    for t in tankstellen:
        tankstellen_list.append(
            [tankstellen[t]["name"] + "-" + tankstellen[t]["place"], t])  # Alle Tankstellen in einer Liste speichern

    return render_template('tankstellen.html', tankstellen=tankstellen_list, usertankstellen=favorites, action=action)


"""Holt die favoriten Tankstellen anhand einer BenutzerID"""
"""Holt die favoriten Tankstellen anhand einer BenutzerID"""


def get_favorites(id):
    usertankstellen = []
    cursor = db.cursor()
    cursor.execute('SELECT tankstellenid FROM Benutzer2Tankstelle where BenutzerID = %s;', (id,))
    for curr in cursor.fetchall():
        usertankstellen.append(curr[0])
    cursor.close()
    db.commit()
    return usertankstellen


"""Updated die favoritisierten Tankstellen für eine BenutzerID id und einer Liste von Tankstellen"""


def update_favorites(id, favorite_tankstellen):
    cursor = db.cursor()
    # Alle Zuordnungen entfernen, anschließend neu zuordnen.
    cursor.execute(
        'DELETE FROM Benutzer2Tankstelle WHERE benutzerID = %s',
        (id,))
    for item in favorite_tankstellen:
        if request.form[item] == 'on':
            cursor.execute('INSERT INTO Benutzer2Tankstelle(BenutzerID, TankstellenID) VALUES (%s, %s)',
                           (id, item[:-9],))
    cursor.close()
    db.commit()


# @page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
# def tankstelle(tankstelle_id):
#     return "Coming soon!"
