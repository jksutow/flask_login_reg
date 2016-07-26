from flask import Flask, render_template, session, redirect, request, flash, url_for
from mysqlconnection import MySQLConnector
import re

from flask.ext.bcrypt import Bcrypt
EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
app = Flask(__name__)
app.secret_key = 'Secretttt'
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'login_db')

@app.route ('/', methods = ["GET"])
def index():
    return render_template('register.html')

@app.route('/users', methods=['POST'])
def create_user():
    error = False
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    pw_hash = bcrypt.generate_password_hash(password)
    pw_confirm = request.form['pw_confirm']
    # run validations and if successful we create pw hash w/ bcrypt
    if len(first_name) < 3:
        error = True
        flash ("First name cannot be blank")
    if len(last_name) < 3:
        error = True
        flash ("Last name cannot be blank")
    if len(password) < 3:
        error = True
        flash("Password cannot be blank")
    if len(pw_confirm) < 3:
        error = True
        flash("Password confirmation cannot be blank")
    if not EMAIL_REGEX.match(email):
        error = True
        flash("Email is invalid")
    if password != pw_confirm:
        error = True
        flash('Passwords do not match')
    if error is True:
        return redirect(url_for('index'))


    insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ('{}','{}', '{}', '{}', NOW(), NOW())".format(first_name, last_name, email, pw_hash)
    query_data = {'first_name': first_name, 'last_name': last_name, 'email': email, 'password': pw_hash}

    mysql.query_db(insert_query, query_data)
    # , query_data)
    return redirect('/')

@app.route('/success', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    query_data = { 'email': email }
    user = mysql.query_db(user_query, query_data) # user will be returned in a list
    email = mysql.query_db(user_query, query_data)[0]
    print email
    if bcrypt.check_password_hash(user[0]['password'], password):
	    return render_template("success.html", email=email)
    else:
		flash("Invalid Password. Please try again.")
    return redirect('/')




app.run(debug=True)
