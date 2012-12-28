# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

from twisted.internet import reactor

import settings, logger, util # ZK stuff
from pysql_wrapper import pysql_wrapper

import re


# Just a const list used in the templates.
def get_languages():
	return ['C++', 'C#', 'Java', 'Node', 'Perl',  'Python', 'Rails', 'Ruby', 'VB', 'VB.NET']


app = Flask(__name__)

def main(api_app, revision_):
	"""Sort of a workaround, but only because of context and whatnot.
		
		api.app has to be passed explicity after everything is imported,
		or else you get all sorts of horrid ImportErrors.
		This is called by zkpm.master

		revision_ is actually just master.revision() passed in, because
		if it isn't passed in, and we try to import master, we get all
		sorts of circular imports, which cause hell. Trust me, it's
		just easier this way.
	"""
	app.jinja_env.globals.update(revision=revision_)
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


"""
If you want to make a page require a login, do this:
@app.route("/example")
def example():
	if not get_login():
		return requires_login()
	return render_template('whatever', this, that, etc)

If you make a form, make sure it's secure! Use le-csrf.
@app.route("/example", methods=["POST", "GET"])
def example():
	if request.method == "POST":
		if not csrf_match():
			csrf_bail('example')
		# Validate form.
	else:
		return render_template('example.html', csrf=csrf_make())

And in your form:
	<input type="hidden" id="le-csrf" 
		name="le-csrf" value="{{ csrf }}" />
"""

@app.route("/")
@app.route("/index")
def index():
	if not get_login():
		return requires_login()
	return render_template('index.html', login=get_username())

@app.route("/login", methods=["POST", "GET"])
def login():
	return render_template('login.html', csrf=csrf_make())

@app.route("/do-login", methods=["POST"])
def do_login():
	if not csrf_match():
		return csrf_bail('login')
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

@app.route("/-test")
def _test():
	print '*'*10
	print store, store.d
	print '*'*10
	return redirect(url_for('index'))


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

def csrf_bail(where, **kwargs):
	flash("Something went wrong. Please try again.", 'error')
	return redirect(url_for(where, **kwargs))

def csrf_match():
	if 'le-csrf' not in request.form \
			or 'le-submit' not in request.form \
			or 'csrf' not in session:
		return False
	# Make sure they iniated this.
	if request.form['le-csrf'] != session['csrf']:
		logger.warning("User", get_username(), "failed csrf tests.", "Possible cross site request attack?")
		del session['csrf']
		return False
	return True

def csrf_make():
	# We use this to make sure the user initiated this.
	# If they didn't, this won't exist in the form, or it'll mismatch.
	csrf = gen_secret()
	session['csrf'] = csrf
	return csrf