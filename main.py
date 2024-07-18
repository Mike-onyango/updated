
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Token selection options
marvel_characters = ['Iron Man', 'Captain America', 'Thor', 'Hulk', 'Black Widow', 'Hawkeye', 'Spider-Man', 'Captain Marvel']

# Routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

# Login
@app.route("/login", methods=["POST"])
def login():
    #more infomation on code 
    username = request.form['username']
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html")

# Sign Up
@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form['username']
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    #use this to check if the login page has another user 
    if user:
        return render_template("index.html", error="User already here!")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)  
        db.session.commit()
        session["username"] = username
        return redirect(url_for("dashboard"))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template('dashboard.html', username=session['username'], marvel_characters=marvel_characters)
    return redirect(url_for('home'))

# Token selection
#the game tokens are gotten here
@app.route('/select_token', methods=["POST"])
def select_token():
    if "username" in session:
        token = request.form['token']
        # Here you can save the selected token to the database or session if needed
        return render_template('dashboard.html', username=session['username'], selected_token=token, marvel_characters=marvel_characters)
    return redirect(url_for('home'))

# Logout
#it will bw found on the last page 
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
