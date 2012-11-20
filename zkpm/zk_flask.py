# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

from twisted.internet import reactor

import settings, logger, util, master # ZK stuff
from pysql_wrapper import pysql_wrapper

import re

app = Flask(__name__)

def main(api_app):
	"""Sort of a workaround, but only because of context and whatnot.
		api.app has to be passed explicity after everything is imported,
		or else you get all sorts of horrid ImportErrors.
		This is called by zkpm.master
	"""
	app.jinja_env.globals.update(revision=master.revision)
	app.register_blueprint(api_app, url_prefix='/api')
	app.debug = settings.DEBUG
	app.secret_key = settings.SECRET_KEY
	expire_check()

def expire_check():
	"""Check for any expired keys, disable them if needed, then wait.
	"""
	import time
	licenses = pysql().get('licenses')
	timestamp = int(time.time())
	logger.debug('Checking for expired licenses.')
	for license in licenses:
		if license['expires'] == 0:
			# Doesn't expire, ignore.
			continue
		if license['expires'] == -1:
			# Already expired, ignore.
			continue
		if int(license['expires']) > timestamp:
			# In the future, ignore.
			continue
		expire_key(license['id'])
	logger.debug('Finished expired license check, waiting for:', settings.EXPIRE_CHECK_TIME)
	reactor.callLater(settings.EXPIRE_CHECK_TIME, expire_check)

def expire_key(id):
	if not pysql().where('id', id).update('licenses', {"expires": -1, "disabled": 1}):
		logger.error("Unable to disable license:", id)
		return
	logger.info("Disabled expired license:", id)


# Just a const list used in the templates.
languages = ['C++', 'C#', 'Java', 'Node', 'Perl',  'Python', 'Rails', 'Ruby', 'VB', 'VB.NET']

"""
If you want to make a page require a login, do this:
@app.route("/example")
def example():
	if not get_login():
		return requires_login()
	return render_template('whatever', this, that, etc)

If you make a form, make sure it's secure! Use le-shiggy-diggy.
@app.route("/example", methods=["POST", "GET"])
def example():
	if request.method == "POST":
		if not shiggy_match():
			shiggy_bail('example')
		# Validate form.
	else:
		return render_template('example.html', shiggy_diggy=shiggy_make())

And in your form:
	<input type="hidden" id="le-shiggy-diggy" 
		name="le-shiggy-diggy" value="{{ shiggy_diggy }}" />
"""

@app.route("/")
@app.route("/index")
def index():
	if not get_login():
		return requires_login()
	return render_template('index.html', login=get_username())

@app.route("/login", methods=["POST", "GET"])
def login():
	return render_template('login.html', shiggy_diggy=shiggy_make())

@app.route("/do-login", methods=["POST"])
def do_login():
	if not shiggy_match():
		return shiggy_bail('login')
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

class Struct:
	def __init__(self, **entries): 
		self.__dict__.update(entries)
# --------------------------------------------------
# Past here: logging in, account management, database connections, etc.
from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension
from contextlib import closing

store = DictStore()
kvsess = KVSessionExtension(store, app) # http://flask-kvsession.readthedocs.org/en/0.3.1/
#kvsess.cleanup_sessions() # Cleanup the old sessions periodically.

def pysql():
	# We'll populate this with the info for both sqlite3 and MySQL.
	# This way, whatever they choose, it'll "Just Work (TM)".
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
	# This is so they can log in as Foo, FOO or fOo.
	username = username.lower()
	return hashlib.sha256(salt + password + username + salt).hexdigest()

def get_http_login():
	return request.authorization is not None

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

def shiggy_bail(where, **kwargs):
	flash("Something went wrong. Please try again.", 'error')
	return redirect(url_for(where, **kwargs))

def shiggy_match():
	if 'le-shiggy-diggy' not in request.form \
			or 'le-submit' not in request.form \
			or 'shiggy_diggy' not in session:
		return False
	# Make sure they iniated this.
	if request.form['le-shiggy-diggy'] != session['shiggy_diggy']:
		logger.warning("User", get_username(), "failed shiggy-diggy tests.", "Possible cross site request attack?")
		del session['shiggy_diggy']
		return False
	return True

def shiggy_make():
	# We use this to make sure the user initiated this.
	# If they didn't, this won't exist in the form, or it'll mismatch.
	shiggy_diggy = gen_secret()
	session['shiggy_diggy'] = shiggy_diggy
	return shiggy_diggy