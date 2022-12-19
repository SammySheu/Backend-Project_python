from flask import Flask, render_template, redirect, request, flash
from package.sqlalchemy_config import setUpDB, addUser

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

User = setUpDB(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return '<h1>Hello world!!</h1>'

@app.route('/member-<username>', methods=['GET'])
@login_required
def member(username):
    
    # To convert class(current_user) to object(user) so that html could read
    user = {
        'username':current_user.username,
        'password':current_user.password,
        'realname':current_user.realname,
        'email':current_user.email
    }
    
    return render_template('memberPage.html', user = user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if(request.method == 'POST'):
        user = User(   
            username = request.form['username'],
            password = request.form['password'],
            realname = request.form['realname'],
            email = request.form['email'],
        )
        searchEmail = User.query.filter_by(email=request.form['email']).first()
        searchUsername = User.query.filter_by(username=request.form['username']).first()
        if not searchEmail and not searchUsername:
            addUser(app, user)
            return redirect('/login')
        elif searchEmail:
            flash('Email already exists')
            return render_template('registerPage.html')
        elif searchUsername:
            flash('This username has been used')
            return render_template('registerPage.html')
    else:
        return render_template('registerPage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        searchData = User.query.filter_by(email=request.form['email']).first()
        if(searchData):
            if (searchData.password == request.form['password']):
                # flash('Success to log in')
                login_user(searchData)
                generatedURL = f'member-{searchData.username}'
                return redirect(generatedURL)
            else:
                flash('Incorrect password')
                return render_template('loginPage.html')
        else:
            flash('No such user was found')
            return render_template('loginPage.html')
    else: 
        return render_template('loginPage.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    # app.run(debug = True, host='0.0.0.0', port=5555)
    app.run(debug=True, host='0.0.0.0', port=5555)