# Flask-login + Flask-sqlalchemy + Docker

Hi, this project is to demonstrate a simple authentication process with flask-login in use. 
Flask-login is a session-based authentication which provides common tasks of login, logout process and remembering user's session over a period of time. I'll later provide an example of token-based authentication using flask-jwt-extended. Hope this could help to compare two type of authentication.

## How to use?

1. Make sure you have docker running on your back. After cloning this branch of this project, you could type in following CMD in your CLI. Everything would be set in a few minutes. 
```Shell
docker-compose up
```

2. Opening your browser and type in
```
http://127.0.0.1:5555/login
```
Now you could interact with my little flask-app(on docker container)!

## Flask-login
[Flask-Login 0.7.0 documentation](https://flask-login.readthedocs.io/en/latest/)
1. To set up its config, followed as official documentation had said.
```python
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
```
2. By the documentation, developer has to provide user_loader callback, which should take an ID of an user and then returning the corresponding user object. In this case, I use flask-sqlalchemy to help searching data in mysql database and then return the corresponding user object in user_loader callback. (explained in sqlalchemy_config.py)

3. As all config had been setting up, developer could login user if user has been examined by its user login information(email and password), and log out if user want to log out. 
```python
# The argument we passed in to login_user() should be an instance of `User` class
login_user(searchData) # searchData is an instance of our 'User' class

logout_user()
```

4. One more thing we have to add is let our custom `User` class inherit UserMixin, which record following properties and methods.
* is_authenticated -> return True if user information has been examined
* is_active -> return True when login user
* is_anonymous -> return False if user is authenticated
* get_id() -> to get user id

In this case, we could just pass UserMixin into class User
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    realname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
```

## Flask-sqlalchemy 
[Flask-SQLAlchemy Documentation(3.0.x)](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension)

1. Since I set up SQLalchemy in another file, I wrapped all the things I need in setUpDB and then return User schema
in app.py
```python
User = setUpDB(app)
# function setUpDB take in app argument and return User Schema
```
whereas in sqlalchemy_config.py, I put all the settings in it. 
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setUpDB(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqldb://{user}:{password}@{host}/{database}'
    app.config['SECRET_KEY']= 'SQLalchemySecretKey'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
    db.init_app(app)

    class User(db.Model, UserMixin):
        # Define User schema here
    return User
```
One thing to mark here is that application will need a driver to speak with mysql database. In the connect string, '+mysqldb' is needed and it indicates that driver 'mysqlclient' take charge and it will help sqlalchemy to speak with MySQL.(If driver MySQL-Connector is in use, the connect string should be `mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>`)

2. Once we define our models and tables, we could call SQLAlchemy.create_all() within application context.
```python
with app.app_context():
    db.create_all()
```

3. Now if we want to query the data, we could use SQLAlchemy.session to execute queries and modify model data.
We should also call SQLAlchemy.session.commit() after modifying any data. 
```python
def addUser(app, user):
    with app.app_context():
        db.session.add(user)
        db.session.commit()
```

## Docker 
There are lots of benefits of using container, and Docker is one of the platform that could help us containerize our application. Here only shows how I configure my container using docker and docker-compose. 

1. Build a python-based container which could serve as our flask-app.
```Dockerfile
FROM python

COPY . /home/app

WORKDIR /home/app

RUN pip3 install --upgrade -r ./requirements.txt

CMD [ "python3", "app.py" ]
```

2. Build a mysql-based container in which we pass our custom environmental variable.
```Dockerfile
FROM mysql

COPY ./database_user.sql /docker-entrypoint-initdb.d

ENV MYSQL_ROOT_PASSWORD=my-secret-pw \
    MYSQL_DATABASE=tradingValley_userdb \
    MYSQL_USER=localUser \
    MYSQL_PASSWORD=password
```
According to mysql's official image, developer could initiate a database with extension file(.sh) provided in `/docker-entrypoint-initdb.d`. I create a table called `user` and insert with test_user to check whether my table was successfully built. 

3. After finished written our Dockerfile, we could use docker-compose to build these two services in once.
And since we're using docker-compose, it will take care the network among two service by creating a default 'bridge' network.
```yaml
services:
  mysql-server:
    build: ./mysql_init
    ports:
      - 3306:3306
    container_name: mysql_container
    volumes:    # Specify the volume so data could be persistent
      - mysql-server_db:/var/lib/mysql
  
  flask-server:
    build: ./
    restart: always
    command: python3 ./app.py;
    depends_on:
      - mysql-server
    ports:
      - 5555:5555
    container_name: flask_container

volumes:
  mysql-server_db:
    driver: local
```
