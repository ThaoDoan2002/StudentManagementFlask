from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$%&*&*%^&$&^'
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:12345678@localhost/studentsdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["YEAR"] = 3
db = SQLAlchemy(app)


login = LoginManager(app)
login.login_view = 'loginUser'
