import mysql
from flask import Blueprint, render_template
from webapp import database

page = Blueprint('karte', __name__, template_folder='templates')

db = database.getDataBaselogin()

"""Generiert die anzuzeigenden Tankstellen und leitet an die Anzeigende html weiter."""


@page.route('/karte')
def show_map():
    # Alle Tankstellen aus der Datenbank holen
    cursor = db.cursor()
    cursor.execute("SELECT id, name, lat, lng FROM Tankstellen")
    data = cursor.fetchall()
    cursor.close()

    # Datenbank Format in JSON interpretieren um mit Javascript die Karte zu generieren
    tankstellen_list = {}
    for t in data:
        tankstellen_list[t[0]] = {
            "name": t[1],
            "coord": {
                "lat": str(t[2]),
                "lng": str(t[3])
            }
        }
    return render_template('karte.html', tankstellen_list=tankstellen_list)
