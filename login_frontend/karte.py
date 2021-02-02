from flask import Blueprint, render_template

page = Blueprint('karte', __name__, template_folder='templates')


@page.route('/karte')
def show_map():
    return render_template('karte.html')
