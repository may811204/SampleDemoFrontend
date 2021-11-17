from flask import Flask, redirect, url_for, render_template, request, flash, session
import mysql.connector as mysql
from functools import wraps
from app import app

MANAGER = "Manager"
INVENTORY_CLERK = "InverntoryClerk"
SALESPERSON = "Salesperson"
SERVICE_WRITER = "ServiceWriter"
ANONYMOUS = "anonymous"
ROLAND_AROUND = "Owner"

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
    db_connection.reconnect()
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
    db_connection.reconnect()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM RegisteredUser WHERE username=%s AND user_password=%s", (username, password))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['username'] = data[0]
            session['role'] = data[4]
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
        password = request.form["password"]
        # cur = mysql.connection.cursor()
        # cur.execute("insert into users(UNAME,UPASS,EMAIL) values(%s,%s,%s)", (name, pwd, email))
        # mysql.connection.commit()
        # cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("register.html", status=status)


@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        vin = request.form["vin"]
        car_type = request.form["car_type"]
        invoice_price = request.form["invoice_price"]
        date_added = request.form["date_added"]
        session['vin'] = vin
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('view_vehicle')
    return render_template("index.html")


@app.route('/view_vehicle', methods=['GET'])
def view_vehicle():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    vin = session['vin']
    cursor.execute("SELECT * FROM Vehicle WHERE VIN=%s", (vin, ))
    row_of_car = cursor.fetchone()
    print("vin of session: ", session, row_of_car)
    print("##################")
    print(row_of_car[0])
    info = {
        'vin': row_of_car[0],
        'invoice_price': row_of_car[1],
        'manu_name': row_of_car[2],
        'inbound_date': row_of_car[3],
        'model_year': row_of_car[4],
        'model_name': row_of_car[5],
        'optional_description': row_of_car[6],
        'vehicle_type': row_of_car[7],
        'vehicle_type_id': row_of_car[8]
    }
    return render_template("vehicle_details.html", params=info)


@app.route('/')
@app.route('/home', methods=['GET'])
@is_logged_in
def index():
    role = session['role']
    if role == MANAGER:
        return render_template("manager.html", params=role)
    elif role == INVENTORY_CLERK:
        return render_template("clerk.html", params=role)
    elif role == SERVICE_WRITER:
        return render_template("writer.html", params=role)
    elif role == SALESPERSON:
        return render_template("salesperson.html", params=role)
    else:
        return render_template('index.html', params=load_vehicles())
