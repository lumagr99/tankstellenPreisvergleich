import json
import urllib

from flask import Flask, render_template

app = Flask(__name__)




@app.route("/")
def index():
    url = "http://127.0.0.1:5000/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    print(data["00060453-0001-4444-8888-acdc00000001"]["name"])
    test_list = ["klaus", "peter", "franz"]
    return render_template('index.html', tankstellen=test_list)


@app.route("/tankstelle/<tankstelle_id>")
def tankstelle(tankstelle_id):
    #tankstelle = Tankstelle.query.get(id)
    return render_template("tankstelle.html", tankstelle=tankstelle_id)


if __name__ == "__main__":
    app.run(port=int(8080), debug=True)