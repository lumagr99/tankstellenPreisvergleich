from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
import string, random

app = Flask(__name__)
app.secret_key = 'FlaskLoginTest'

app.config['MYSQL_HOST'] = '45.88.109.79'
app.config['MYSQL_USER'] = 'tankstellenCrawler'
app.config['MYSQL_PASSWORD'] = 'qGD0zc5iKsvhyjwO'
app.config['MYSQL_DB'] = 'tankdaten'

mysql = MySQL(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        benutzername = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Benutzer WHERE benutzername = %s', (benutzername,))
        account = cursor.fetchone()
        if account['password'] == hash_sha256(password + account['salt']):
            session['loggedin'] = True
            session['id'] = account['id']
            session['benutzername'] = account['benutzername']
            return 'Du hast dich erfolgreich eingeloggt!'
        else:
            msg = 'Ups, das war wohl nichts!'
    return render_template('index.html', msg=msg)


def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('benutzername', None)
    return redirect(url_for('login'))


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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
        mysql.connection.commit()
        msg = 'Du wurdest erfolgreich Registriert!'
    return msg


"""Hasht einen angegeben String mit SHA 256."""


def hash_sha256(text_string):
    text_string = hashlib.sha256(text_string.encode()).hexdigest()
    return text_string


app.run()
