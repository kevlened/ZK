# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g, redirect, url_for, flash
import settings
from pysql_wrapper import pysql_wrapper

app = Flask(__name__)
app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY

'''If you want to make a page require a login, do this:
@app.route("/example")
def example():
	if not get_login():
		return requires_login()
	return render_template('whatever', this, that, etc)
'''

@app.route("/")
@app.route("/index")
def index():
	if not get_login():
		return requires_login()
	return render_template('index.html', login=get_username())

@app.route("/login", methods=["POST", "GET"])
def login():
	return render_template('login.html')

@app.route("/do-login", methods=["POST", "GET"])
def do_login():
	return requires_login()

@app.route("/logout")
def logout():
	session.destroy()
	return redirect(url_for('index'))

@app.route("/secret")
@app.route("/secret/<int:length>")
def secret(length=20):
	'''Generate a secret code for them to copy.
	'''
	import string, random
	secret = ''.join(random.choice(string.printable[:-6]) for x in range(length))
	resp = app.make_response('It\'s dangerous to go alone, here, take this:\n' + secret)
	resp.mimetype = 'text/plain'
	return resp

@app.route("/manage/app")
def app_manage():
	abort(418)

@app.route("/manage/key")
def key_manage():
	abort(418)

# --------------------------------------------------
# Past here: logging in, account management, database connections, etc.
from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension
from contextlib import closing
import sqlite3

store = DictStore()
kvsess = KVSessionExtension(store, app) # http://flask-kvsession.readthedocs.org/en/0.3.1/
#kvsess.cleanup_sessions() # Cleanup the old sessions periodically.

def pysql():
	# We'll populate this with the info for both sqlite3 and MySQL.
	# This way, whatever they choose, it'll Just Work (TM).
	pysql_conf = {
		"db_type": settings.DATABASE_TYPE,
		"db_path": settings.DATABASE_PATH,
		"db_host": settings.DATABASE_HOST,
		"db_user": settings.DATABASE_USER,
		"db_pass": settings.DATABASE_PASS,
		"db_name": settings.DATABASE_NAME,
	}
	return pysql_wrapper(**pysql_conf)

def hash_pass(username, password, salt = settings.PASSWORD_SALT):
	import hashlib
	username = username.lower() # Regardless of casing, provides the same hash.
	return hashlib.sha256(salt + password + username + salt).hexdigest()

@app.before_request
def before_request():
	pass

@app.teardown_request
def teardown_request(exception):
	pass

def get_login():
	'''True or False depending on if the user is authenticated.
	'''
	return session.get("logged_in", None) is not None

def get_username():
	return session.get("username", None)

def requires_login(return_page=None):
	if session.get("logged_in", None) is not None:
		# Already logged in? Back to the index for you!
		return redirect(url_for('index'))
	
	# Everything is prefixed with 'le' to make people cringe.
	if request.method == "POST":
		if 'le-username' not in request.form or 'le-password' not in request.form:
			flash('Something went wrong.', 'error')
			return redirect(url_for('login'))
		username = request.form['le-username']
		password = request.form['le-password']
		records = pysql().where('username', username).where('password', hash_pass(username, password)).get('users')
		if len(records) != 1:
			flash("Sorry, the username or password was incorrect.", 'error')
			return redirect(url_for('login'))
		else: # correct-a-mundo!
			records = records[0] # We want the dictionary!
			session['username'] = records['username']
			session['logged_in'] = True
			session.regenerate()
			return redirect(url_for('index'))
	else:
		return redirect(url_for('login'))
