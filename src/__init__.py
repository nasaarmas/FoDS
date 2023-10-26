from flask import Flask
from src.database_connection import DatabaseConnection

app = Flask(__name__, static_folder='./static')
db = DatabaseConnection(dbname="usos2", user="postgres",
                        password="haslo", host="localhost", port="5432")

from src.flask_bp.dashboard import dash_bp
from src.flask_bp.admin import admin_bp
from src.flask_bp.manager import manager_bp
from src.flask_bp.courses import courses_bp
from src.flask_bp.author import author_bp
from src.flask_bp.teacher import teacher_bp
from src.flask_bp.login import login_bp


app.register_blueprint(dash_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/')
app.register_blueprint(manager_bp, url_prefix='/')
app.register_blueprint(courses_bp, url_prefix='/')
app.register_blueprint(author_bp, url_prefix='/')
app.register_blueprint(teacher_bp, url_prefix='/')
app.register_blueprint(login_bp, url_prefix='/')

