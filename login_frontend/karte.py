import json
import urllib

from flask import Blueprint, render_template

page = Blueprint('karte', __name__, template_folder='templates')

backend_url_prefix = "http://127.0.0.1:5000"

"""Generiert die anzuzeigenden Tankstellen und leitet an die Anzeigende html weiter."""

@page.route('/karte')
def show_map():
    url = backend_url_prefix + "/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen
    tankstellen_list = {}
    for t in data:
        tankstellen_list[t] = {
            "name": data[t]["name"],
            "coord": {
                "lat": data[t]['coord']['lat'],
                "lng": data[t]['coord']['lng']
            }
        }

    return render_template('karte.html', tankstellen_list=tankstellen_list)
