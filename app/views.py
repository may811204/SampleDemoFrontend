from flask import Flask, redirect, url_for, render_template, request, flash, session, jsonify
import mysql.connector as mysql
from functools import wraps
from app.constants import Colors, Manufacturer, VehicleTypes
from app.sql import *
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
"""
Christie
"""


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login with correct credential', 'danger')
            return redirect(url_for('login'))

    return wrap


def roland_login_as_other(session, r):
    cur_role = session['role']
    next_role = session.get('switch_to_role', None)
    return cur_role == ROLAND_AROUND and next_role and next_role == r


def calculate_available_vehicles():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(AvailableVehicles)
    available_vehicles = cursor.fetchone()
    return available_vehicles[0]

"""
Christie
"""


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

"""
Christie
"""
def load_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByManufacturer)
    sales_by_manufacturer = cursor.fetchall()
    cursor.execute(SalesByType)
    sales_by_type = cursor.fetchall()
    cursor.execute(SalesByColor)
    sales_by_color = cursor.fetchall()
    cursor.execute(PartStatistics)
    part_statistics = cursor.fetchall()
    data = {
        'sales_by_manufacturer' : sales_by_manufacturer,
        'sales_by_type' : sales_by_type,
        'sales_by_color' : sales_by_color,
        'part_statistics' : part_statistics
    }
    return data

"""
Christie
"""
@app.route("/sales_by_manufacturer", methods=["GET"])
def sales_by_manufacturer_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByManufacturer)
    sales_by_manufacturer = cursor.fetchall()
    return render_template('reports/sales_by_manufacturer.html', records=sales_by_manufacturer)

"""
Christie
"""

@app.route("/sales_by_type", methods=["GET"])
def sales_by_type_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByType)
    sales_by_type = cursor.fetchall()
    return render_template('reports/sales_by_type.html', records=sales_by_type)


"""
Christie
"""

@app.route("/part_stats", methods=["GET"])
def part_stats_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(PartStatistics)
    part_stats = cursor.fetchall()
    return render_template('reports/part_stats.html', records=part_stats)

"""
Christie
"""
@app.route("/below_cost", methods=["GET"])
def below_cost_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DummySQL)
    below_cost = cursor.fetchall()
    return render_template('reports/below_cost.html', records=below_cost)

"""
Christie
"""
@app.route("/gross_income", methods=["GET"])
def gross_income_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DummySQL)
    gross_income = cursor.fetchall()
    return render_template('reports/gross_income.html', records=gross_income)

"""
Christie
"""
@app.route("/monthly_sale", methods=["GET"])
def monthly_sale_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DummySQL)
    monthly_sale = cursor.fetchall()
    return render_template('reports/monthly_sale.html', records=monthly_sale)

"""
Christie
"""
@app.route("/repair_reports", methods=["GET"])
def repair_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DummySQL)
    repair_reports = cursor.fetchall()
    return render_template('reports/repair_reports.html', records=repair_reports)

"""
Christie
"""
@app.route("/avg_inventory", methods=["GET"])
def avg_inventory_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DummySQL)
    avg_inventory = cursor.fetchall()
    return render_template('reports/avg_inventory.html', records=avg_inventory)

"""
Christie
"""

@app.route("/sales_by_color", methods=["GET"])
def sales_by_color_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByColor)
    sales_by_color = cursor.fetchall()
    return render_template('reports/sales_by_color.html', records=sales_by_color)



"""
Christie
"""

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


"""
Christie
"""


# logout
@app.route("/logout")
def logout():
    if 'switch_to_role' in session:
        session.pop('switch_to_role')
        return redirect('home')
    else:
        session.clear()
        flash('You are now logged out', 'success')
    return redirect(url_for('login'))


"""
Christie
"""


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


"""
Christie
"""

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        vin = request.form["vin"]
        invoice_price = request.form["invoice_price"]
        manu_name = request.form["manu_name"]
        inbound_date = request.form["inbound_date"]
        model_year = request.form["model_year"]
        model_name = request.form["model_name"]
        optional_description = request.form["optional_description"]
        vehicleTypeID = request.form["vehicleTypeID"]
        vehicleInputterID = request.form["vehicleInputterID"]
        session['vin'] = vin
        cur = db_connection.cursor()
        cur.execute("insert into Vehicle(VIN, invoice_price, manu_name, inbound_date, model_year, model_name, optional_description, vehicleTypeID, vehicleInputterID)\
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (vin, invoice_price, manu_name, inbound_date, model_year, model_name, optional_description, vehicleTypeID, vehicleInputterID))
        db_connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('view_vehicle')
    return render_template("vehicle.html")

"""
Christie
"""


@app.route('/add_customer', methods=['POST', 'GET'])
def add_customer():
    if request.method == 'POST':
        print(request.form)
        street_address = request.form["street_address"]
        is_individual = request.form['is_individual']
        if is_individual == "0":
            return redirect('add_individual')
        else:
            return redirect('add_business')
    return render_template('register_customer.html')


"""
Christie
"""


@app.route('/add_individual', methods=['POST', 'GET'])
def add_individual():
    if request.method == 'POST':
        print(request.form)
        flash('Individual added', 'success')
    return render_template('register_individual.html')


"""
Christie
"""


@app.route('/add_business', methods=['POST', 'GET'])
def add_business():
    if request.method == 'POST':
        print(request.form)
        flash('Business added', 'success')
    return render_template('register_business.html')


"""
Christie
"""


@app.route('/view_vehicle', methods=['GET'])
def view_vehicle():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    vin = session['vin']
    cursor.execute("SELECT * FROM Vehicle WHERE VIN=%s", (vin,))
    row_of_car = cursor.fetchone()
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


"""
Christie
"""


@app.route("/search_data", methods=["POST", "GET"])
def public_search():
    if request.method == 'POST':
        vin = request.form['vin']
        vehicle_type = request.form['vehicle_type']
        manufacturer = request.form['manufacturer']
        model_year = request.form['model_year']
        color = request.form['color']
        list_price = request.form['list_price']
        key_word = request.form['key_word']
        print("[Search data]: search filters: ", vin, vehicle_type, manufacturer, model_year, color, list_price,
              key_word)
        db_connection.reconnect()
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Vehicle WHERE VIN=%s", (vin,))
        matches = cursor.fetchall()
        records = []
        for m in matches:
            info = {
                'vin': m[0],
                'invoice_price': m[1],
                'manu_name': m[2],
                'inbound_date': m[3],
                'model_year': m[4],
                'model_name': m[5],
                'optional_description': m[6],
                'vehicle_type': m[7],
                'vehicle_type_id': m[8]
            }
            records.append(info)
    return render_template("manager_filter_results.html", records=records)


"""
Christie
"""


@app.route("/search_customer", methods=["POST", "GET"])
def search_customer():
    db_connection.reconnect()
    if request.method == 'POST':
        driver_license = request.form['driver_license']
        tax_id = request.form['tax_id']
        cursor = db_connection.cursor()
        cursor.execute(FilterCustomer, (driver_license,))
        customers = cursor.fetchall()
        print("[Search Customer]: driver license: {}, tax_id: {}".format(driver_license, tax_id))
        records = []
        for customer in customers:
            info = {
                'customer_id': customer[0],
                'street_address': customer[1],
                'city': customer[2],
                'state': customer[3],
                'postal_code': customer[4],
                'email': customer[5],
                'phone': customer[6],
                'is_individual': customer[7]
            }
            records.append(info)
    return render_template("customer_filter_results.html", records=records)



@app.route("/switch_role", methods=["POST"])
def switch_role():
    session['switch_to_role'] = request.form['switch']
    print(session)
    return redirect(request.referrer)



"""
Christie
"""


@app.route('/home', methods=['GET'])
@is_logged_in
def index():
    role = session['role']
    s = roland_login_as_other(session, MANAGER)
    print("roland_login_as_other: ", s)
    if role == MANAGER or roland_login_as_other(session, MANAGER):
        available_car_amount = calculate_available_vehicles()
        return render_template("manager.html", colors=Colors, manufacturers=Manufacturer, vehicles_types=VehicleTypes, available_car_amount=available_car_amount)
    elif role == INVENTORY_CLERK or roland_login_as_other(session, INVENTORY_CLERK):
        return render_template("clerk.html", params=role)
    elif role == SERVICE_WRITER or roland_login_as_other(session, SERVICE_WRITER):
        return render_template("writer.html", params=role)
    elif role == SALESPERSON or roland_login_as_other(session, SALESPERSON):
        return render_template("salesperson.html", params=role)
    elif role == ROLAND_AROUND:
        return render_template('roland.html', colors=Colors, manufacturers=Manufacturer, vehicles_types=VehicleTypes)
