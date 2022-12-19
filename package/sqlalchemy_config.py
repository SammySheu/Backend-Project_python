from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
load_dotenv()
from flask_login import UserMixin

db = SQLAlchemy()

def setUpDB(app):
    # global db

    host=os.environ.get('mysql_local_host')
    database=os.environ.get('mysql_local_database')
    user=os.environ.get('mysql_local_user')
    password=os.environ.get('mysql_local_password')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqldb://{user}:{password}@{host}/{database}'
    app.config['SECRET_KEY']= 'helloworld'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
    db.init_app(app)

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        password = db.Column(db.String(150), nullable=False)
        realname = db.Column(db.String(50), nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
    with app.app_context():
        db.create_all()
    return User

def addUser(app, user):
    with app.app_context():
        db.session.add(user)
        db.session.commit()