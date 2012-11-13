# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g, redirect, url_for, flash
import settings, logger, util # ZK stuff
from pysql_wrapper import pysql_wrapper
import re

app = Flask(__name__)
app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY

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
	<input type="hidden" id="le-shiggy-diggy" name="le-shiggy-diggy" value="{{ shiggy_diggy }}" />
"""

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
		if not shiggy_match():
			return shiggy_bail('app_add')
		import re
		le_name = request.form['le-name'][:64]
		if not re.match('^[a-zA-Z0-9_\-]+$', le_name):
			flash("Sorry, app names can only include alphanumeric characters, dashes and underscores.", 'error')
			return redirect(url_for('app_add'))

		le_language = request.form['le-language'][:32]
		if le_language == "Other":
			le_language = request.form['le-other-language'][:32] # If they specify Other, grab le-other-language.
		if not re.match('^[a-zA-Z0-9_\-]+$', le_language):
			flash("Sorry, languages can only include alphanumeric characters, dashes and underscores.", 'error')
			return redirect(url_for('app_add'))
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
		return render_template('apps.add.html', login=get_username(), languages=languages, shiggy_diggy=shiggy_make())

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
		if not shiggy_match():
			return shiggy_bail('app_edit', id=id)
		type_ = request.form['le-type']
		if type_ not in ('name', 'language', 'active', 'version'):
			return flash_wrong(id)

		if type_ == "name":
			if 'le-name' not in request.form:
				return flash_wrong(id)
			name = request.form['le-name'][:64] # Trim if needed.
			if not re.match('^[a-zA-Z0-9_\-]+$', le_name):
				flash("Sorry, app names can only include alphanumeric characters, dashes and underscores.", 'error')
				return redirect(url_for('app_edit', id=id))
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
			if not re.match('^[a-zA-Z0-9_\-]+$', le_name):
				flash("Sorry, languages can only include alphanumeric characters, dashes and underscores.", 'error')
				return redirect(url_for('app_edit', id=id))

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
		"def_language": app['language'] in languages,
		"shiggy_diggy": shiggy_make()
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
		if not shiggy_match():
			return shiggy_bail('app_manage')
		if not pysql().where('id', id).delete('apps'):
			logger.error("Unable to delete app", id)
			flash("Unable to delete app. Please try again.", 'error')
			return redirect(url_for('app_manage'))
		if not pysql().where('app', id).delete('licenses'):
			logger.error("Unable to delete licenses for app", id)
			flash("Unable to delete licenses for app.", 'warning')
		logger.info("Successfully deleted app", id)
		flash("Successfully deleted app.", 'success')
		return redirect(url_for('app_manage'))

	app = app[0] # Grab the dict.
	app['users'] = len(pysql().where('app', app['id']).get('licenses'))

	extra = {
		"login": get_username(),
		"app": Struct(**app),
		"id": id,
		"shiggy_diggy": shiggy_make()
	}
	return render_template('apps.remove.html', **extra)

@app.route("/key")
@app.route("/key/")
def key_redir():
	return redirect(url_for('key_manage'))

@app.route("/key/manage")
def key_manage():
	if not get_login():
		return requires_login()
	keys_ = pysql().get('licenses')
	keys = []
	for key in keys_:
		app = pysql().where('id', key['app']).get('apps')
		if len(app) != 1:
			continue
		key['app_str'] = app[0]['name']
		key['expires'] = util.expires_str(key['expires'])
		keys.append(Struct(**key))
	return render_template('keys.manage.html', login=get_username(), keys=keys)

@app.route("/key/add", methods=["POST", "GET"])
def key_add():
	if not get_login():
		return requires_login()

	if request.method == "POST":
		if not shiggy_match():
			return shiggy_bail('key_add')
		for le_part in ('le-app', 'le-user', 'le-needs-hwid', 'le-active', 
						'le-expires', 'le-expires-select', 'le-expires-years',
						'le-expires-months', 'le-expires-weeks', 'le-expires-days', 'le-expires-hours'
						'le-aban', 'le-submit', 'le-license-style', 'le-email'):
			if le_part not in request.form:
				return redirect(url_for('key_add'))
		le_app = request.form['le-app']
		try:
			le_app = int(le_app)
		except ValueError as e:
			return redirect(url_for('key_add'))
		app = pysql().where('id', le_app).get('apps')
		if len(app) != 1:
			return redirect(url_for('key_add'))

		le_user = request.form['le-user']
		if not re.match('^[a-zA-Z0-9_\-]+$', le_user):
			flash("Sorry, usernames can only include alphanumeric characters, dashes and underscores.", 'error')
			return redirect(url_for('key_add', id=id))
		le_email = request.form['le-email']
		if len(le_email) > 0 and not re.match(r'''^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$''', le_email):
			flash("Sorry, that email isn't valid.", 'error')
			return redirect(url_for('key_add', id=id))
		le_needs_hwid = 1 if request.form['le-needs-hwid'] == "yes" else 0
		le_disabled = 0 if request.form['le-active'] == "yes" else 1
		le_expires = 0
		if request.form['le-expires-select'] == "yes":
			exp_str = '{0}y{1}m{2}w{3}d{4}h'.format(
					request.form['le-expires-years'],
					request.form['le-expires-months'],
					request.form['le-expires-weeks'],
					request.form['le-expires-days'],
					request.form['le-expires-hours']
				)
			le_expires = util.timestamp_from_str(exp_str)

		le_aban = 1 if request.form['le-aban'] == "yes" else 0

		key = util.key_from_style(request.form['le-license-style'], app=app[0]['name'])
		data = {
			"app": le_app,
			"user": le_user,
			"email": le_email,
			"key": key,
			"needs_hwid": le_needs_hwid,
			"hwid": "",
			"disabled": le_disabled,
			"expires": le_expires,
			"aban": le_aban,
		}
		pysql_ = pysql()
		if not pysql_.insert('licenses', data):
			logger.error("Unable to add new key.")
			flash("Something went wrong. Please try again.", 'error')
			return redirect(url_for('key_add'))
		flash('You just created this key. You can edit it here.', 'success')
		return redirect(url_for('key_edit', id=pysql_._cursor.lastrowid))
	else:
		apps = []
		for app_ in pysql().get('apps'):
			app = {
				"id": app_['id'],
				"name": app_['name']
			}
			apps.append(Struct(**app))
		return render_template('keys.add.html', login=get_username(), apps=apps, shiggy_diggy=shiggy_make())

@app.route("/key/edit")
@app.route("/key/edit/<int:id>", methods=["POST", "GET"])
def key_edit(id=None):
	if not get_login():
		return requires_login()
	if id is None:
		return redirect(url_for('key_manage'))
	key = pysql().where('id', id).get('licenses')
	if len(key) != 1:
		return redirect(url_for('key_manage'))
	
	def flash_wrong(id):
		# Simple temp def to flash an error and redirect.
		logger.error("Something went wrong updating license", id)
		flash("Something went wrong.", 'warning')
		return redirect(url_for('key_edit', id=id))

	if request.method == "POST":
		if 'le-type' not in request.form or 'le-submit' not in request.form:
			return flash_wrong(id)
		if not shiggy_match():
			return shiggy_bail('key_edit', id=id)
		type_ = request.form['le-type']
		if type_ not in ('app', 'name', 'email', 'license',
						 'needs-hwid', 'hwid', 'disabled', 'expires'):
			return flash_wrong(id)

		if type_ == "app":
			if 'le-app' not in request.form:
				return flash_wrong(id)
			app_id = request.form['le-app']
			app = pysql().where('id', app_id).get('apps')
			if len(app) != 1:
				return flash_wrong(id)
			app = app[0]
			if not pysql().where('id', id).update('licenses', {"app": app['id']}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully updated associated app.", 'success')

		elif type_ == "name":
			if 'le-name' not in request.form:
				return flash_wrong(id)
			name = request.form['le-name'][:64] # Trim if needed.
			if not re.match('^[a-zA-Z0-9_\-]+$', name):
				flash("Sorry, usernames can only include alphanumeric characters, dashes and underscores.", 'error')
				return redirect(url_for('key_edit', id=id))
			if not pysql().where('id', id).update('licenses', {"user": name}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully updated license username.", 'success')

		elif type_ == "email":
			if 'le-email' not in request.form:
				return flash_wrong(id)
			email = request.form['le-email'][:64] # Trim if needed.
			if len(email) > 0 and not re.match(r'''^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$''', email):
				flash("Sorry, that email is not valid.", 'error')
				return redirect(url_for('key_edit', id=id))
			if not pysql().where('id', id).update('licenses', {"email": email}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully updated license email.", 'success')

		elif type_ == "license":
			license = util.key_from_style()
			if not pysql().where('id', id).update('licenses', {"key": license}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully regenerated license key.", 'success')

		elif type_ == "needs-hwid":
			if 'le-needs-hwid' not in request.form:
				return flash_wrong(id)
			needs_hwid = 1 if request.form['le-needs-hwid'] == "yes" else 0
			if not pysql().where('id', id).update('licenses', {"needs_hwid": needs_hwid}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully updated license.", 'success')

		elif type_ == "hwid":
			if not pysql().where('id', id).update('licenses', {"hwid": ""}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully reset HWID.", 'success')

		elif type_ == "disabled":
			if 'le-disabled' not in request.form:
				return flash_wrong(id)
			disabled = 1 if request.form['le-disabled'] == "yes" else 0
			if not pysql().where('id', id).update('licenses', {"disabled": disabled}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully {} key.".format('disabled' if disabled == 1 else 'enabled'), 'success')

		elif type_ == "expires":
			if 'le-expires-select' not in request.form:
				return flash_wrong(id)
			le_expires = 0
			if request.form['le-expires-select'] == "yes":
				exp_str = '{0}y{1}m{2}w{3}d{4}h'.format(
						request.form['le-expires-years'],
						request.form['le-expires-months'],
						request.form['le-expires-weeks'],
						request.form['le-expires-days'],
						request.form['le-expires-hours']
					)
				le_expires = util.timestamp_from_str(exp_str)
			if not pysql().where('id', id).update('licenses', {"expires": le_expires}):
				return flash_wrong(id)
			key = pysql().where('id', id).get('licenses')
			flash("Successfully updated expiration.", 'success')

		logger.info("Successfully updated app", id)

	key = key[0] # Grab the dict.
	apps = []
	for app in pysql().get('apps'):
		app['selected'] = True if app['id'] == key['app'] else False
		apps.append(Struct(**app)) 

	expires_dict = util.expires_dict(key['expires'])
	key['expires_'] = Struct(**expires_dict)
	extra = {
		"login": get_username(),
		"key": Struct(**key),
		"apps": apps,
		"id": id,
		"shiggy_diggy": shiggy_make()
	}
	return render_template('keys.edit.html', **extra)

@app.route("/key/remove")
@app.route("/key/remove/<int:id>", methods=["POST", "GET"])
def key_remove(id=None):
	if not get_login():
		return requires_login()
	if id is None:
		return redirect(url_for('key_manage'))

	key = pysql().where('id', id).get('licenses')
	if len(key) != 1:
		return redirect(url_for('key_manage'))

	if request.method == "POST":
		if not shiggy_match():
			return shiggy_bail('key_manage')
		if not pysql().where('id', id).delete('licenses'):
			logger.error("Unable to delete license", id)
			flash("Unable to delete license. Please try again.", 'error')
			return redirect(url_for('key_manage'))
		logger.info("Successfully deleted license", id)
		flash("Successfully deleted license.", 'success')
		return redirect(url_for('key_manage'))

	key = key[0] # Grab the dict.
	key['app'] = pysql().where('id', key['app']).get('apps')[0]['name']
	key['disabled'] = "Yes" if key['disabled'] == 1 else "No"
	key['expires'] = util.expires_str(key['expires'])

	extra = {
		"login": get_username(),
		"key": Struct(**key),
		"id": id,
		"shiggy_diggy": shiggy_make()
	}
	return render_template('keys.remove.html', **extra)

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