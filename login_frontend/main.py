from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import string
import random
import dotenv
import os

from login_frontend import tankstellenliste, karte, tankstelle, Database
import mysql.connector



db = Database.getDataBaselogin()

db.ping(True)
app = Flask(__name__)

app.register_blueprint(tankstellenliste.page)
app.register_blueprint(karte.page)
app.register_blueprint(tankstelle.page)
app.secret_key = 'FlaskLoginTest'


"""Verwaltet den Login eines Benutzers."""
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        benutzername = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM Benutzer WHERE benutzername = %s', (benutzername,))
        account = cursor.fetchone()
        cursor.close()
        db.commit()
        if account[2] == hash_sha256(password + account[3]):
            session['loggedin'] = True
            session['id'] = account[0]
            session['benutzername'] = account[1]
            return redirect(url_for('tankstellenliste.show'))
        else:
            msg = 'Ups, das war wohl nichts!'
    return render_template('login.html', msg=msg)


"""Verwaltet den Logout eines Benutzers."""


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('benutzername', None)
    return redirect(url_for('start'))


"""Verwaltet die Registrierung eines neuen Benutzers."""


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password' in request.form:
        benutzername = request.form['username']
        password = request.form['password']
        msg = createAccount(benutzername, password)
    elif request.method == 'POST':
        msg = 'Füll bitte das Formular aus!'

    return render_template('register.html', msg=msg)


"""Validiert ob ein Account existiert, wenn nicht erstellt es ihn.
Gibt eine passende Fehlermeldung zurück.
Generiert zum Passwort einen Salt und Hasht die kombination beider."""


def createAccount(benutzername, password):
    msg = ''
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Benutzer WHERE benutzername = %s', (benutzername,))
    account = cursor.fetchone()

    if account:
        msg = 'Die Daten gibts leider schon!'
    elif not benutzername or not password:
        msg = 'Füll bitte das Formular aus!'
    else:
        # Account existiert nicht

        # generiert salt
        salt = ''.join(random.sample(string.ascii_lowercase, 10))
        cursor.execute('INSERT INTO Benutzer(benutzername, password, salt) VALUES (%s, %s, %s)',
                       (benutzername, hash_sha256(password + salt), salt,))
        cursor.close()
        msg = 'Du wurdest erfolgreich Registriert!'
    db.commit()
    return msg


"""Hasht einen angegeben String mit SHA 256."""


def hash_sha256(text_string):
    text_string = hashlib.sha256(text_string.encode()).hexdigest()
    return text_string


"""Definiert die Startseite"""


@app.route('/')
def start():
    return render_template('start.html')


@app.route('/about')
def about():
    return render_template('about.html')


app.run(port=int(8080), debug=True)
