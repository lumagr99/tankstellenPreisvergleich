import mysql
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response, request, Blueprint, session
import io
import numpy as np
from datetime import date, datetime, timedelta, time
from webapp import database
import time

page = Blueprint('tankstelle', __name__, template_folder='templates')

db = database.getDataBaselogin()

backend_url_prefix = "http://localhost"

tankstellen_id = ""

"""Funktion zur Rückgabe der Preisdaten einer Tankstelle.
   Rückgabe als list
   Author: Graef, Kloos"""


def get_preis_data(tankstellen_id, begin="2021-02-01 00:00:00", end="2021-02-01 23:59:59"):
    cursor = db.cursor()
    cursor.execute("SELECT id, round(avg(e5), 3) as e5, round(avg(e10), 3) as e10, round(avg(diesel), 3) as diesel, "
                   "CONCAT(HOUR(timedate), ':' , MINUTE(timedate)) as hours FROM Preise where id = %s and "
                   "timedate between %s and %s group by hours, id", (tankstellen_id, begin, end,))
    data = cursor.fetchall()
    cursor.close()
    return data


"""Funktion zur Rückgabe der viertel Stundenweisen Durchschnittspreise.
   Author: Graef, Kloos, Rust"""


def get_preis_avg(begin="2021-01-17 00:00:00", end="2021-01-17 23:59:59"):
    cursor = db.cursor()
    cursor.execute("SELECT round(avg(e5), 2) as e5, round(avg(e10), 2) as e10, round(avg(diesel), 2) as diesel, "
                   "CONCAT(HOUR(timedate), ':',MINUTE(timedate)) as hours FROM `Preise` where timedate between %s and %s "
                   "group by hours order by timedate;", (begin, end,))
    result = cursor.fetchall()
    cursor.close()
    return result


"""Funktion zum zeichnen eines Plots der Preisentwicklung einer Tankstelle.
   Author: Kloos"""


@page.route("/plot_png/<tankstelle_id>/<datum>/<display_e5_avg>/<display_e10_avg>/<display_diesel_avg>")
def plot_png(tankstelle_id, datum, display_e5_avg, display_e10_avg, display_diesel_avg):
    begin = datum + " 00:00:00"
    end = datum + " 23:59:59"  # beginn und ende des PReisverlaufs festlegen

    preis_data = get_preis_data(tankstelle_id, begin, end)  # Preise abfragen

    # Überprüfen, ob die Jehweiligen Duschnittspreise angezeigt werden sollen
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

    # Preise nach Sorten aufteilen
    preise_e5 = []
    preise_e10 = []
    preise_diesel = []
    preise_e5_avg = []
    preise_e10_avg = []
    preise_diesel_avg = []
    zeiten = []

    for zeit in preis_data:
        zeiten.append(zeit)
        preise_e5.append(zeit[1])
        preise_e10.append(zeit[2])
        preise_diesel.append(zeit[3])

    # Wenn notwendig durchschnittspreise zuordnen
    if display_e5_avg or display_e10_avg or display_diesel_avg:
        avg_data = get_preis_avg(begin, end)
        for zeit in avg_data:
            preise_e5_avg.append(zeit[0])
            preise_e10_avg.append(zeit[1])
            preise_diesel_avg.append(zeit[2])

    # Aufrufen der Funktion zum erstellen des Graphen
    fig = create_figure(zeiten, preise_e5, preise_e10, preise_diesel, preise_e5_avg, preise_e10_avg, preise_diesel_avg,
                        display_e5_avg, display_e10_avg, display_diesel_avg)
    output = io.BytesIO()  # Graph erstellen und auf Canvas bringen
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')  # URL für Graph(png) zuruckgeben


"""Funktion zurkontrolle, ob der Preis einer sorten duchgänig 0 ist
   Author: Kloos"""


def preis_is_zero(preis_list):
    zero_count = 0
    for preis in preis_list:
        if preis == 0:
            zero_count += 1
    return zero_count == len(preis_list)


"""Funktion zu erstellung eines Plots aus den gegebenen daten einer Tankstelle.
   Author: Kloos"""


def create_figure(zeiten, preis_e5, preis_e10, preis_diesel, preise_e5_avg, preise_e10_avg, preise_diesel_avg,
                  display_e5_avg, display_e10_avg, display_diesel_avg):
    # Uhrzeiten zu einem Array hinzufügen um diese später für die X-Achse als Beschriftung zu nutzen
    zeiten_achse = []
    for zeit in zeiten:
        zeiten_achse.append(str(float(zeit[4].split(":")[0]) + float(zeit[4].split(":")[1]) / 60))
    zeiten_achse.sort(key=float)

    # Umwandeln der Preislisten in Numpy-Arrays
    p_e5 = np.array(preis_e5)
    p_e10 = np.array(preis_e10)
    p_diesel = np.array(preis_diesel)

    # Plot initialisieren
    fig, ax = plt.subplots()

    # Überprüfen, ob ein Preis duchgänig null ist sonst den PReisververlauf plotten
    if not preis_is_zero(p_e5):
        ax.plot(zeiten_achse, p_e5, label="E5", color="blue")
    if not preis_is_zero(p_e10):
        ax.plot(zeiten_achse, p_e10, label="E10", color="red")
    if not preis_is_zero(p_diesel):
        ax.plot(zeiten_achse, p_diesel, label="Diesel", color="green")

    # Überprüfung ob die Duschnitsspreise angezeigt werden sollen, und wenn ja diese plotten
    if display_e5_avg:
        p_e5_avg = np.array(preise_e5_avg)
        ax.plot(zeiten_achse, p_e5_avg, label="E5 Duchschnitt", linestyle=(0, (5, 2)), color="blue")

    if display_e10_avg:
        p_e10_avg = np.array(preise_e10_avg)
        ax.plot(zeiten_achse, p_e10_avg, label="E10 Duchschnitt", linestyle=(0, (5, 2)), color="red")

    if display_diesel_avg:
        p_diesel_avg = np.array(preise_diesel_avg)
        ax.plot(zeiten_achse, p_diesel_avg, label="Diesel Duchschnitt", linestyle=(0, (5, 2)), color="green")

    # Festlegen der Achsen beschriftung, Titel und position der Legende
    ax.set(xlabel='Zeit (h)', ylabel='Preis (€)',
           title='Preisverlauf')
    ax.legend(loc='upper left')

    # nur jeden vierten wert aus t benutzen (volle Stunden)
    X_TICKS = 4
    plt.xticks(range(0, len(zeiten_achse), X_TICKS), zeiten_achse[::X_TICKS], rotation=(45),
               fontsize=(5))

    # Rastter auf Diagramm erstellen und Hintergrundfarbe des Diagramms anpassen
    ax.grid()
    ax.set(facecolor="#e1ebf4")
    fig.set(facecolor="#e1ebf4")
    return fig


"""seite mit Der Preisentwicklung einer Tankstelle.
   Author: Kloos"""


@page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
def tankstelle(tankstelle_id):
    tankstellen_id = tankstelle_id
    # Tankstellendaten holen
    cursor = db.cursor()
    cursor.execute("SELECT id, name, place, postCode, street, houseNumber FROM Tankstellen WHERE ID=%s",
                   (tankstelle_id,))
    data = cursor.fetchone()
    cursor.close()

    # Standartgemäßig die Duschnitspreise nicht anzeigen lassen
    display_e5_avg = False
    display_e10_avg = False
    display_diesel_avg = False

    # Zeitraum zwischen jetzt und den letzten 15 minuten festlegen, damit auf jeden FallDaten vorhanden sind
    now = datetime.now()
    end = str(now.date()) + " " + str(now.time())[0:8]
    fifteen_minutes = timedelta(minutes=15)
    begin = str(now.date()) + " " + str((now - fifteen_minutes).time())[0:8]

    # Aktuelle Preise holen
    preise = get_preis_data(tankstelle_id, begin, end)
    preis_e5 = ""
    preis_e10 = ""
    preis_diesel = ""
    for zeit in preise:
        preis_e5 = zeit[1]
        preis_e10 = zeit[2]
        preis_diesel = zeit[3]

    # Überprüfen ob Benutzer eingeloggt
    benutzerid = ""
    if 'loggedin' in session:
        benutzerid = session.get('id')

    # Darzustellende Informationen zusammenstellen
    info = {
        "name": data[1] + " " + data[2],
        "postcode": data[3],
        "place": data[2],
        "street": data[4],
        "houseNumber": data[5],
        "id": tankstelle_id
    }

    preise = {
        "diesel": preis_diesel,
        "e5": preis_e5,
        "e10": preis_e10
    }

    now = datetime.today().strftime("%Y-%m-%d")
    # Fall: PUT-Request: dinbestimmtes Datum / Duschnitspreis wurde angewählt oder die Tankstelle wurde als Favorit gekennzeichnet
    if 'tag' in request.form:
        # Überprüfen, welche Duchschnitspreise anugewählt wurden
        if request.form.get("e5_avg"):
            display_e5_avg = True
        if request.form.get("e10_avg"):
            display_e10_avg = True
        if request.form.get("diesel_avg"):
            display_diesel_avg = True

        # Das anzuzeigenen Datum auf das vom Nutzer ausgewählte setzen
        temptime = request.form.get("datum")
        print(now, temptime)
        # Überprüfen ob das augewählte Datum vor dem 01.02.2021 liegt: falls ja Datum auf 01.02.2021 setzen
        if time.mktime(datetime.strptime(temptime, "%Y-%m-%d").timetuple()) < \
                time.mktime(
                    datetime.strptime("2021-02-01", "%Y-%m-%d").timetuple()):  # Datum muss nach dem 01.02.2021 sein
            now = "2021-02-01"
        # Überprüfen ob das Datum vor dem heutigen liegt
        elif time.mktime(datetime.strptime(temptime, "%Y-%m-%d").timetuple()) < \
                time.mktime(
                    datetime.strptime(now, "%Y-%m-%d").timetuple()):
            now = temptime


        # Favoriten Status übernehmen
        fav = request.form.get("favorit")

        cursor = db.cursor()
        cursor.execute('DELETE FROM Benutzer2Tankstelle where BenutzerID = %s AND TankstellenID = %s;',
                       (benutzerid, tankstellen_id,))
        if fav:
            cursor.execute('INSERT INTO Benutzer2Tankstelle(BenutzerID, TankstellenID) VALUES (%s, %s);',
                           (benutzerid, tankstellen_id,))
        cursor.close()

    # Seiten mit entsprechende Variablen zurückgeben
    return render_template("tankstelle.html", info=info, datum=now, e5_avg=display_e5_avg,
                           e10_avg=display_e10_avg, diesel_avg=display_diesel_avg, preise=preise,
                           markedFav=isFavorite(benutzerid, tankstellen_id))


"""Fragt ab ob ein Benutzer eine bestimmte Tankstelle favorisiert hat.
   Author: Graef, Rust"""


def isFavorite(benutzerid, tankstellenid):
    if benutzerid != "" and tankstellenid != "":
        cursor = db.cursor()
        cursor.execute("SELECT tankstellenID FROM Benutzer2Tankstelle WHERE benutzerID=%s and tankstellenID = %s;",
                       (benutzerid, tankstellenid,))
        if len(cursor.fetchall()) == 1:
            return True
        cursor.close()
    return False
