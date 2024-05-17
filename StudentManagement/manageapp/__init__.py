from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$%&*&*%^&$&^'
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:%s@localhost/studentsdb?charset=utf8mb4" % quote("p@ssw0rd2002")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["YEAR"] = 3
db = SQLAlchemy(app)


login = LoginManager(app)
login.login_view = 'loginUser'
