from datetime import datetime, timedelta

import mysql.connector
from flask import Blueprint, render_template, session, request, redirect, url_for
from webapp import database

page = Blueprint('tankstellenliste', __name__, template_folder='templates')

db = database.getDataBaselogin()
db.ping(True)

"""Zeigt eine Übersicht über alle Tankstellen.
Ermöglicht das zuordnen von Favoriten.
Nicht mehr direkt für den Benutzer über die Navigation zu errreichen. Hauptsächlich für Debug Zwecke."""


@page.route('/tankstellen', methods=['GET', 'POST'])
def show():
    benutzerid = "-1"
    if 'loggedin' in session:  # Wenn eingeloggt, BenutzerID zuweisen
        benutzerid = session.get('id')

    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute("SELECT id, name, place FROM Tankstellen")
        data = cursor.fetchall()
        cursor.close()

        # Liste von Tankstellen anzeigen
        return show_tankstellen(data, get_favorites(benutzerid), "tankstellenliste.show")

    if request.method == 'POST':
        if benutzerid != "-1":
            update_favorites(benutzerid, request.form)  # Aktualisierungen verarbeiten.
            # Get request auf die show methode zum aktualisieren der Anzeige
            return redirect(url_for('tankstellenliste.show'))

    return redirect(url_for('start'))


"""Generiert eine Favoritenliste."""


@page.route('/favoriten', methods=['GET', 'POST'])
def favorites():
    if 'loggedin' in session:  # Nur für eingeloggte Benutzer möglich
        if request.method == 'GET':
            benutzerid = session.get('id')  # BenutzerID zuweisen

            cursor = db.cursor()
            # Nur favorisierte Tankstellen mit aktuellen Preisen holen
            now = datetime.now()
            end = str(now.date()) + " " + str(now.time())[0:8]
            begin = str(now.date()) + " " + str((now - timedelta(minutes=15)).time())[0:8]
            cursor.execute(
                "select Tankstellen.id, Tankstellen.name, Tankstellen.place, Preise.e5, Preise.e10, Preise.diesel FROM Tankstellen "
                "join Benutzer2Tankstelle ON Benutzer2Tankstelle.TankstellenID = Tankstellen.id "
                "join Preise ON Tankstellen.id = Preise.id "
                "WHERE Benutzer2Tankstelle.BenutzerID = %s "
                "AND Preise.timedate BETWEEN %s AND %s "
                "ORDER BY Preise.timedate DESC", (benutzerid, begin, end,))
            data = cursor.fetchall()
            cursor.close()

            # Seite laden
            return show_tankstellen(data, get_favorites(benutzerid), "tankstellenliste.favorites")

        if request.method == 'POST':
            update_favorites(session.get('id'), request.form)  # Aktualisierungen verarbeiten.
            return redirect(url_for('tankstellenliste.favorites'))
        return redirect(url_for('tankstellenliste.show'))
    return redirect(url_for('start'))


"""Übergibt die notwendigen Daten."""


def show_tankstellen(tankstellen, favorites, action):
    return render_template('tankstellen.html', tankstellen=tankstellen, usertankstellen=favorites, action=action)


"""Holt die favoriten Tankstellen anhand einer BenutzerID"""


def get_favorites(benutzerid):
    usertankstellen = []
    cursor = db.cursor()
    cursor.execute('SELECT tankstellenid FROM Benutzer2Tankstelle where BenutzerID = %s;', (benutzerid,))
    for curr in cursor.fetchall():
        usertankstellen.append(curr[0])
    cursor.close()
    db.commit()
    return usertankstellen


"""Aktualisiert die favoritisierten Tankstellen für eine BenutzerID id und einer Liste von Tankstellen"""


def update_favorites(benutzerid, favorite_tankstellen):
    cursor = db.cursor()
    # Alle Zuordnungen entfernen, anschließend neu zuordnen.
    cursor.execute(
        'DELETE FROM Benutzer2Tankstelle WHERE benutzerID = %s',
        (benutzerid,))
    for item in favorite_tankstellen:
        if request.form[item] == 'on':
            cursor.execute('INSERT INTO Benutzer2Tankstelle(BenutzerID, TankstellenID) VALUES (%s, %s)',
                           (benutzerid, item[:-9],))
            print(cursor.statement)
    cursor.close()
    db.commit()
