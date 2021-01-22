import json
import urllib

from flask import Flask, render_template

app = Flask(__name__)




@app.route("/")
def index():
    url = "localhost:5000/tankstellen"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    test_list = ["klaus", "peter"]
    return render_template('index.html', tankstellen=test_list)


@app.route("/tankstelle/<tankstelle_id>")
def tankstelle(tankstelle_id):
    #tankstelle = Tankstelle.query.get(id)
    return render_template("tankstelle.html", tankstelle=tankstelle_id)


if __name__ == "__main__":
    app.run(port=int(8080), debug=True)