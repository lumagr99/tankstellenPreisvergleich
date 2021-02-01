import urllib
import json

from flask import Blueprint, render_template

page = Blueprint('tankstellenliste', __name__, template_folder='templates')

backend_url_prefix = "http://127.0.0.1:5000"


@page.route('/tankstellen', methods=['GET', 'POST'])
def show():
    url = backend_url_prefix + "/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())  # Alle Tankstellen aus Backend abfragen

    tankstellen_list = []
    for t in data:
        tankstellen_list.append(
            [data[t]["name"] + "-" + data[t]["place"], t])  # Alle Tankstellen in einer Liste speichern

    return render_template('tankstellen.html', tankstellen=tankstellen_list)


@page.route("/tankstelle/<tankstelle_id>", methods=['GET', 'POST'])
def tankstelle(tankstelle_id):
    return "Coming soon."
