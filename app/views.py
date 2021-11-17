from flask import Flask, redirect, url_for, render_template, request, flash, session
import mysql.connector as mysql
from functools import wraps
from app import app

MANAGER = "manager"
INVENTORY_CLERK = "clerk"
SALESPERSON = "sales"
SERVICE_WRITER = "writer"
ANONYMOUS = "anonymous"
ROLAND_AROUND = "roland"

db_connection = mysql.connect(host='50.87.253.41', database='charljl4_jj', user='charljl4_team007', password='team007',
                              port=3306)


# https://github.com/ashishsarkar/UserLogin/blob/master/app.py
# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login with correct credential', 'danger')
            return redirect(url_for('login'))

    return wrap


def load_vehicles():
    d = {}
    print("Connected to:", db_connection.get_server_info())
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM Vehicle;")
    vehicles = cursor.fetchall()
    for i, vehicle in enumerate(vehicles):
        v = {
            'id': vehicle[0],
            'price': vehicle[1],
            'manufacturer': vehicle[2]
        }
        d[i] = v
    return d


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM RegisteredUser WHERE username=%s AND user_password=%s", (username, password))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['username'] = data[0]
            flash('Login Successfully', 'success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again', 'danger')
            return render_template("login.html")
    else:
        return render_template("login.html")


# logout
@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    status = False
    if request.method == 'POST':
        name = request.form["username"]
        email = request.form["email"]
        pwd = request.form["password"]
        # cur = mysql.connection.cursor()
        # cur.execute("insert into users(UNAME,UPASS,EMAIL) values(%s,%s,%s)", (name, pwd, email))
        # mysql.connection.commit()
        # cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("register.html", status=status)


@app.route("/<user>")
@is_logged_in
def user(user):
    if user == MANAGER:
        return render_template("manager.html", params=user)
    elif user == INVENTORY_CLERK:
        return render_template("manager.html", params=user)
    elif user == SERVICE_WRITER:
        return render_template("manager.html", params=user)
    else:
        return render_template("author.html", params=user)


@app.route('/')
@app.route('/home', methods=['GET'])
@is_logged_in
def index():
    return render_template('index.html', params=load_vehicles())
