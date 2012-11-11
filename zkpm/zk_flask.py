# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g, redirect, url_for, flash
import settings, logger # ZK stuff
from pysql_wrapper import pysql_wrapper

app = Flask(__name__)
app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY

# Just a const list used in the templates.
languages = ['C++', 'C#', 'Java', 'Node', 'Perl', 
			 'Python', 'Rails', 'Ruby', 'VB', 'VB.NET']

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
	secret = gen_secret(length)
	resp = app.make_response('It\'s dangerous to go alone, here, take this:\n' + secret)
	resp.mimetype = 'text/plain'
	return resp

def gen_secret(length=20):
	import string, random
	return ''.join(random.choice(string.printable[:-6]) for x in range(length))

@app.route("/app")
@app.route("/app/")
def app_redir():
	return redirect(url_for('app_manage'))

@app.route("/app/manage")
def app_manage():
	if not get_login():
		return requires_login()
	apps_ = pysql().get('apps')
	apps = []
	for app in apps_:
		app['users'] = len(pysql().where('app', app['id']).get('licenses'))
		apps.append(Struct(**app))
	return render_template('apps.manage.html', login=get_username(), apps=apps)

@app.route("/app/add", methods=["GET", "POST"])
def app_add():
	if not get_login():
		return requires_login()

	if request.method == "POST":
		for le_part in ('le-name', 'le-language', 'le-active', 'le-submit'):
			if le_part not in request.form:
				return redirect(url_for('app_add'))
		le_name = request.form['le-name'][:64]
		le_language = request.form['le-language'][:32]
		if le_language == "Other":
			le_language = request.form['le-other-language'][:32] # If they specify Other, grab le-other-language.
		le_active = 1 if request.form['le-active'] == "yes" else 0
		import time
		data = {
			"name": le_name,
			"language": le_language,
			"active": le_active,
			"version": int(time.time())
		}
		pysql_ = pysql()
		if not pysql_.insert('apps', data):
			logger.error("Unable to create new app.")
			flash("Something went wrong. Please try again.", 'error')
			return redirect(url_for('app_add'))
		flash('You just created this app. You can edit it here.', 'success')
		return redirect(url_for('app_edit', id=pysql_._cursor.lastrowid))
	else:
		return render_template('apps.add.html', login=get_username(), languages=languages)

@app.route("/app/edit")
@app.route("/app/edit/<int:id>", methods=["POST", "GET"])
def app_edit(id=None):
	if not get_login():
		return requires_login()
	if id is None:
		return redirect(url_for('app_manage'))
	app = pysql().where('id', id).get('apps')
	if len(app) != 1:
		return redirect(url_for('app_manage'))
	
	def flash_wrong(id):
		# Simple temp def to flash an error and redirect.
		logger.error("Something went wrong updating app", id)
		flash("Something went wrong.", 'warning')
		return redirect(url_for('app_edit', id=id))

	if request.method == "POST":
		if 'le-type' not in request.form or 'le-submit' not in request.form:
			return flash_wrong(id)
		type_ = request.form['le-type']
		if type_ not in ('name', 'language', 'active', 'version'):
			return flash_wrong(id)

		if type_ == "name":
			if 'le-name' not in request.form:
				return flash_wrong(id)
			name = request.form['le-name'][:64] # Trim if needed.
			if not pysql().where('id', id).update('apps', {"name": name}):
				return flash_wrong(id)
			app = pysql().where('id', id).get('apps')
			flash("Successfully updated app name.", 'success')

		elif type_ == "language":
			if 'le-language' not in request.form or 'le-other-language' not in request.form:
				return flash_wrong(id)
			language = request.form['le-language'][:32]
			if language == "Other":
				language = request.form['le-other-language'][:32] # Trim if needed.
			if not pysql().where('id', id).update('apps', {"language": language}):
				return flash_wrong(id)
			app = pysql().where('id', id).get('apps')
			flash("Successfully updated app language.", 'success')

		elif type_ == "active":
			if 'le-active' not in request.form:
				return flash_wrong(id)
			active = 1 if request.form['le-active'] == "yes" else 0
			if not pysql().where('id', id).update('apps', {"active": active}):
				return flash_wrong(id)
			app = pysql().where('id', id).get('apps')
			flash("Successfully updated app activity.", 'success')

		elif type_ == "version":
			import time
			# Versions are simply a UNIX epoch timestamp.
			# This allows checking if your version is ahead, behind, up-to-date, etc.
			if not pysql().where('id', id).update('apps', {"version": int(time.time())}):
				return flash_wrong(id)
			app = pysql().where('id', id).get('apps')
			flash("Successfully pushed app update.", 'success')

		logger.info("Successfully updated app", id)

	app = app[0] # Grab the dict.
	extra = {
		"login": get_username(),
		"app": Struct(**app),
		"id": id,
		"languages": languages,
		"def_language": app['language'] in languages
	}
	return render_template('apps.edit.html', **extra)

@app.route("/app/remove")
@app.route("/app/remove/<int:id>", methods=["POST", "GET"])
def app_remove(id=None):
	if not get_login():
		return requires_login()
	if id is None:
		return redirect(url_for('app_manage'))

	app = pysql().where('id', id).get('apps')
	if len(app) != 1:
		return redirect(url_for('app_manage'))

	if request.method == "POST":
		if 'le-shiggy-diggy' not in request.form \
				or 'le-submit' not in request.form \
				or 'shiggy_diggy' not in session:
			flash("Something went wrong. Please try again.", 'error')
			return redirect(url_for('app_manage'))
		# Make sure they iniated this.
		if request.form['le-shiggy-diggy'] != session['shiggy_diggy']:
			logger.warning("User", get_username(), "failed app deletion session tests.", "Hijack attempt?")
			del session['shiggy_diggy']
			flash("Something went wrong. Please try again.", 'error')
			return redirect(url_for('app_manage'))
		if not pysql().where('id', id).delete('apps'):
			logger.error("Unable to delete app", id)
			flash("Unable to delete app. Please try again.", 'error')
			return redirect(url_for('app_manage'))
		logger.info("Successfully deleted app", id)
		flash("Successfully deleted app.", 'success')
		return redirect(url_for('app_manage'))

	app = app[0] # Grab the dict.
	app['users'] = len(pysql().where('app', app['id']).get('licenses'))

	# We use this to make sure the user initiated this.
	# If they didn't, this won't exist in the form, or it'll mismatch.
	shiggy_diggy = gen_secret()
	session['shiggy_diggy'] = shiggy_diggy
	extra = {
		"login": get_username(),
		"app": Struct(**app),
		"id": id,
		"shiggy_diggy": shiggy_diggy
	}
	return render_template('apps.remove.html', **extra)

@app.route("/key")
@app.route("/key/")
def key_redir():
	return redirect(url_for('key_manage'))

@app.route("/key/manage")
def key_manage():
	abort(418)

@app.route("/key/add")
def key_add():
	abort(418)

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

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

	if request.method == "POST":
		if 'le-username' not in request.form or 'le-password' not in request.form:
			flash('Something went wrong.', 'error')
			return redirect(url_for('login'))
		username = request.form['le-username']
		password = request.form['le-password']
		records = pysql().where('login', username.lower()).where('password', hash_pass(username, password)).get('users')
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
