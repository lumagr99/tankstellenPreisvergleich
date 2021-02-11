import json
import urllib

import mysql
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response, request, Blueprint, session
import io
import numpy as np
from datetime import date, datetime, timedelta

page = Blueprint('tankstelle', __name__, template_folder='templates')

db = mysql.connector.connect(
    host="45.88.109.79",
    user="tankstellenCrawler",
    password="qGD0zc5iKsvhyjwO",
    database="tankdaten",
    autocommit=True
)
db.ping(True)

backend_url_prefix = "http://localhost"

tankstellen_id = ""

"""Funktion zur Rückgabe der Preis daten einer Tankstelle"""


def get_preis_data(tankstellen_id, begin="2021-01-17%2000:00:00", end="2021-01-17%2023:59:59"):
    url = "http://127.0.0.1:5000/preise?filter=id&begin=" + begin + "&end=" + end + "&interval=hourmin&id=" + tankstellen_id
    response = urllib.request.urlopen(url)
    preis_data = json.loads(response.read())
    return preis_data


"""Funktion zum zeichnen eines Plots der Preisentwicklung einer Tankstelle"""


@page.route("/plot_png/<tankstelle_id>/<datum>/<display_e5_avg>/<display_e10_avg>/<display_diesel_avg>")
def plot_png(tankstelle_id, datum, display_e5_avg, display_e10_avg, display_diesel_avg):
    beginn = datum + "%2000:00:00"
    end = datum + "%2023:59:59"  # beginn und ende des PReisverlaufs festlegen

    preis_data = get_preis_data(tankstelle_id, beginn, end)  # Preise abfragen

    if display_e5_avg == "True":
        display_e5_avg = True
    else:
        display_e5_avg = False
    if display_e10_avg == "True":
        display_e10_avg = True
    else:
        display_e10_avg = False
    if display_diesel_avg == "True":
        display_diesel_avg = True
    else:
        display_diesel_avg = False

    preise_e5 = []
    preise_e10 = []  # Preise nach Sorten aufteilen
    preise_diesel = []
    preise_e5_avg = []
    preise_e10_avg = []
    preise_diesel_avg = []
    zeiten = []
    for zeit in preis_data:
        zeiten.append(zeit)
        preise_e5.append(preis_data[zeit][tankstelle_id]["e5"]["price"])
        preise_e10.append(preis_data[zeit][tankstelle_id]["e10"]["price"])
        preise_diesel.append(preis_data[zeit][tankstelle_id]["diesel"]["price"])
        if display_e5_avg:
            preise_e5_avg.append(preis_data[zeit]["AVG"]["e5"])
        if display_e10_avg == True:
            preise_e10_avg.append(preis_data[zeit]["AVG"]["e10"])
        if display_diesel_avg == True:
            preise_diesel_avg.append(preis_data[zeit]["AVG"]["diesel"])

    fig = create_figure(zeiten, preise_e5, preise_e10, preise_diesel, preise_e5_avg, preise_e10_avg, preise_diesel_avg,
                        display_e5_avg, display_e10_avg, display_diesel_avg)
    output = io.BytesIO()  # Graph erstellen und auf Canvas bringen
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')  # URL für Graph(png) zuruckgeben


"""Funktion zu erstellung eines Plots"""


def create_figure(zeiten, preis_e5, preis_e10, preis_diesel, preise_e5_avg, preise_e10_avg, preise_diesel_avg,
                  display_e5_avg, display_e10_avg, display_diesel_avg):
    t = []
    for zeit in zeiten:
        t.append(str(float(zeit.split(":")[0]) + float(zeit.split(":")[1]) / 60))
    t.sort(key=float)

    p_e5 = np.array(preis_e5)  # Umwandeln der Preislisten in Numpy-Arrays
    p_e10 = np.array(preis_e10)
    p_diesel = np.array(preis_diesel)

    fig, ax = plt.subplots()

    zero_count = 0
    for preis in p_e5:
        if preis == 0:
            zero_count += 1
    if zero_count != len(p_e5):
        ax.plot(t, p_e5, label="E5", color="blue")

    zero_count = 0
    for preis in p_e10:
        if preis == 0:  # Überprüfen, ob der preis einer Sorte duchgänig 0 ist, sonst Plotten der Sortenpreise
            zero_count += 1
    if zero_count != len(p_e10):
        ax.plot(t, p_e10, label="E10", color="red")

    zero_count = 0
    for preis in p_diesel:
        if preis == 0:
            zero_count += 1
    if zero_count != len(p_diesel):
        ax.plot(t, p_diesel, label="Diesel", color="green")

    if display_e5_avg:
        p_e5_avg = np.array(preise_e5_avg)
        ax.plot(t, p_e5_avg, label="E5 Duchschnitt", linestyle=(0, (5, 2)), color="blue")

    if display_e10_avg:
        p_e10_avg = np.array(preise_e10_avg)
        ax.plot(t, p_e10_avg, label="E10 Duchschnitt", linestyle=(0, (5, 2)), color="red")

    if display_diesel_avg:
        p_diesel_avg = np.array(preise_diesel_avg)
        ax.plot(t, p_diesel_avg, label="Diesel Duchschnitt", linestyle=(0, (5, 2)), color="green")

    ax.set(xlabel='Zeit (h)', ylabel='Preis (€)',
           title='Preisverlauf')  # Festlegen der Achsen beschriftung, Titel und position der Legende
    ax.legend(loc='upper left')

    X_TICKS = 4
    plt.xticks(range(0, len(t), X_TICKS), t[::X_TICKS], rotation=(45),
               fontsize=(10))  # nur jeden vierten wert aus t benutzen (volle Stunden)

    ax.grid()
    return fig


"""seite mit Der Preisentwicklung einer Tankstelle"""


@page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
def tankstelle(tankstelle_id):
    tankstellen_id = tankstelle_id
    url = backend_url_prefix + ":5000/tankstellen?id=" + tankstelle_id
    response = urllib.request.urlopen(url)  # Abfragen der Tankstellendaten aus dem Backend
    tankstellen_data = json.loads(response.read())

    tankstelle = tankstellen_data[tankstellen_id]["name"]

    display_e5_avg = False
    display_e10_avg = False
    display_diesel_avg = False

    now = datetime.now()
    end = str(now.date()) + "%20" + str(now.time())[0:8]
    fifteen_minutes = timedelta(minutes=15)
    beginn = str(now.date()) + "%20" + str((now - fifteen_minutes).time())[0:8]

    preise = get_preis_data(tankstelle_id, beginn, end)
    for zeit in preise:
        preis_e5 = (preise[zeit][tankstelle_id]["e5"]["price"])
        preis_e10 = (preise[zeit][tankstelle_id]["e10"]["price"])
        preis_diesel = (preise[zeit][tankstelle_id]["diesel"]["price"])

    datum = ""
    id = ""
    if 'loggedin' in session:
        id = session.get('id')

    # TODO Favoriten überprüfen
    if request.method == "GET":
        datum = date.today()  # Überprüfen ob ein Spezielles Datum über POST mitgegeben wir, sonst standart wert verwenden
        return render_template("tankstelle.html", tankstelle=tankstelle,
                               tankstelle_id=tankstellen_id, datum=datum, e5_avg=display_e5_avg,
                               e10_avg=display_e10_avg,
                               diesel_avg=display_diesel_avg, preis_e5=preis_e5, preis_e10=preis_e10,
                               preis_diesel=preis_diesel, markedFav=isFavorite(id, tankstellen_id))
    else:
        if 'tag' in request.form:  # Fall: es soll ein bestimmter Tag angezeigt werden
            if request.form.get("e5_avg") == "on":
                display_e5_avg = True
            if request.form.get("e10_avg"):
                display_e10_avg = True
            if request.form.get("diesel_avg"):
                display_diesel_avg = True
            datum = request.form.get("datum")
            #return render_template("tankstelle.html", tankstelle=tankstelle,
                                   #tankstelle_id=tankstellen_id, datum=datum, e5_avg=display_e5_avg,
                                   #e10_avg=display_e10_avg,
                                   #diesel_avg=display_diesel_avg, preis_e5=preis_e5, preis_e10=preis_e10,
                                   #preis_diesel=preis_diesel, markedFav=isFavorite(id, tankstellen_id))

          # Fall: Favoriten Status änderung angefragt
            fav = request.form.get("favorit")
            id = session.get('id')
            cursor = db.cursor()
            cursor.execute('DELETE FROM Benutzer2Tankstelle where BenutzerID = %s AND TankstellenID = %s;',
                           (id, tankstellen_id,))
            if fav == "on":
                print("on")
                cursor.execute('INSERT INTO Benutzer2Tankstelle(BenutzerID, TankstellenID) VALUES (%s, %s);',
                               (id, tankstellen_id,))
            cursor.close()
            print(tankstellen_id)
            return render_template("tankstelle.html", tankstelle=tankstelle,
                                   tankstelle_id=tankstellen_id, datum=datum, e5_avg=display_e5_avg,
                                   e10_avg=display_e10_avg,
                                   diesel_avg=display_diesel_avg, preis_e5=preis_e5, preis_e10=preis_e10,
                                   preis_diesel=preis_diesel, markedFav=isFavorite(id, tankstellen_id))


"""Fragt ab ob ein Benutzer eine bestimmte Tankstelle favorisiert hat."""


def isFavorite(benutzerID, tankstellenid):
    if benutzerID != "" and tankstellenid != "":
        cursor = db.cursor()
        cursor.execute("SELECT tankstellenID FROM Benutzer2Tankstelle WHERE benutzerID=%s and tankstellenID = %s;",
                       (benutzerID, tankstellenid,))
        if len(cursor.fetchall()) == 1:
            return True
        cursor.close()
    return False
