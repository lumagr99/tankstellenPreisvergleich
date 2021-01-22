import json
import urllib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template
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
    url = "http://localhost:5000/preise?filter=id&" + "begin" + "2021-01-17%2000:00:00" + "end" + "2021-01-17%2023:59:59" + "&interval=hours&id=" + tankstellen_id
    response = urllib.request.urlopen(url)
    preis_data = json.loads(response.read())
    return preis_data


#def plot(preise):





@app.route("/tankstelle/<tankstelle_id>")
def tankstelle(tankstelle_id):
    url = "http://127.0.0.1:5000/tankstellen?filter=id&id=" + tankstelle_id
    response = urllib.request.urlopen(url)
    tankstellen_data = json.loads(response.read())
    print(tankstelle_id)
    preis_data = get_preis_data(tankstelle_id)
    preise_e5 =[]
    for zeit in preis_data:
        preise_e5.append(preis_data[zeit][tankstelle_id]["e5"]["price"])
    print(preis_data["0"][tankstelle_id]["e5"]["price"])

    plt.plot([1, 2, 3, 4, 5])
    plt.ylabel('some numbers')

    plt.savefig('static/images/plot2.png')


    return render_template("tankstelle.html", tankstelle=tankstellen_data[tankstelle_id]["name"], url="/static/images/plot2.png")



if __name__ == "__main__":
    app.run(port=int(8080), debug=True)