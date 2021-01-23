import json
import urllib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response
import io
import numpy as np

app = Flask(__name__)




@app.route("/")
def index():
    url = "http://127.0.0.1:5000/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    print(data["00060453-0001-4444-8888-acdc00000001"]["name"])

    test_list = []
    for tanke in data:
        test_list.append([data[tanke]["name"] + "-" + data[tanke]["place"], tanke])

    return render_template('index.html', tankstellen=test_list)


def get_preis_data(tankstellen_id, beginn="2021-01-17 00:00:00", end="2021-01-17 23:59:59"):
    url = "http://127.0.0.1:5000/preise?filter=id&begin2021-01-17%2000:00:00end2021-01-17%2023:59:59&interval=hours&id=00062381-330f-4444-8888-acdc00000001"
    response = urllib.request.urlopen(url)
    preis_data = json.loads(response.read())
    print(preis_data)
    return preis_data


@app.route("/plot_png/<tankstelle_id>")
def plot_png(tankstelle_id):

    print(tankstelle_id)
    preis_data = get_preis_data(tankstelle_id)
    print(len(preis_data))
    preise_e5 = []
    preise_e10 = []
    preise_diesel = []
    for zeit in preis_data:
        print(preis_data[zeit][tankstelle_id]["e5"]["price"])
        preise_e5.append(preis_data[zeit][tankstelle_id]["e5"]["price"])
        preise_e10.append(preis_data[zeit][tankstelle_id]["e10"]["price"])
        preise_diesel.append(preis_data[zeit][tankstelle_id]["diesel"]["price"])
    print(preise_e5)

    fig = create_figure(preise_e5, preise_e10, preise_diesel)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure(preis_e5, preis_e10, preis_diesel):
    t = np.array(range(0, 24))
    p_e5 = np.array(preis_e5)
    p_e10 = np.array(preis_e10)

    p_diesel = np.array(preis_diesel)

    fig, ax = plt.subplots()
    ax.plot(t, p_e5, label="E5")
    ax.plot(t, p_e10, label="test")
    ax.plot(t, p_diesel)
    ax.set(xlabel='zeit (h)', ylabel='preis (€)',
           title='Preisverlauf')
    ax.grid()

    return fig




@app.route("/tankstelle/<tankstelle_id>")
def tankstelle(tankstelle_id):
    url = "http://127.0.0.1:5000/tankstellen?filter=id&id=" + tankstelle_id
    response = urllib.request.urlopen(url)
    tankstellen_data = json.loads(response.read())
    #print(preis_data["0"][tankstelle_id]["e5"]["price"])




    return render_template("tankstelle.html", tankstelle=tankstellen_data[tankstelle_id]["name"], tankstelle_id=tankstelle_id)



if __name__ == "__main__":
    app.run(port=int(8080), debug=True)