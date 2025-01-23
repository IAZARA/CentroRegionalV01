from flask import render_template, Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/dashboard')
def dashboard():
    return render_template('main/dashboard.html')
