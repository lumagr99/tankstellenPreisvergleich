import mysql.connector
from flask import Blueprint, render_template, session, request, redirect, url_for

page = Blueprint('tankstellenliste', __name__, template_folder='templates')

db = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="qGD0zc5iKsvhyjwO",
    database="tankdaten",
    autocommit=True
)
db.ping(True)

"""Zeigt eine Übersicht über alle Tankstellen.
Ermöglicht das zuordnen von Favoriten."""


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
        return show_tankstellen(benutzerid, data, get_favorites(benutzerid), "tankstellenliste.show")

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
            # Nur favorisierte Tankstellen holen
            cursor.execute(
                "SELECT id, name, place FROM Tankstellen JOIN Benutzer2Tankstelle on "
                "Benutzer2Tankstelle.TankstellenID = Tankstellen.id where Benutzer2Tankstelle.BenutzerID = %s",
                (benutzerid,))
            data = cursor.fetchall()
            cursor.close()

            # Seite laden
            return show_tankstellen(benutzerid, data, get_favorites(benutzerid), "tankstellenliste.favorites")

        if request.method == 'POST':
            update_favorites(session.get('id'), request.form)  # Aktualisierungen verarbeiten.
            return redirect(url_for('tankstellenliste.favorites'))
        return redirect(url_for('tankstellenliste.show'))
    return redirect(url_for('start'))


"""Übergibt die notwendigen Daten."""


def show_tankstellen(tankstellen, favorites, action):
    tankstellen_list = []
    print(tankstellen)
    for t in tankstellen:
        tankstellen_list.append(
            [t[1] + "-" + t[2], t[0]])  # Alle Tankstellen in einer Liste speichern

    return render_template('tankstellen.html', tankstellen=tankstellen_list, usertankstellen=favorites, action=action)


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
    cursor.close()
    db.commit()
