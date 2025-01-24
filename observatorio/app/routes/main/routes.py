from flask import render_template, Blueprint
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')

@main.route('/map')
@login_required
def map_view():
    return render_template('main/geomap.html')
