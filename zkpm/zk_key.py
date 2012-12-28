# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

import settings, logger, util
import zk_flask as zk
from zk_flask import get_login, requires_login, pysql, Struct
from zk_flask import get_username, csrf_make, csrf_match, csrf_bail

import re

app = zk.app

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
		expired = True if key['expires'] == -1 else False
		key['expires'] = util.expires_str(key['expires'], key['id'], expired)
		keys.append(Struct(**key))
	return render_template('keys.manage.html', login=get_username(), keys=keys)

@app.route("/key/add", methods=["POST", "GET"])
def key_add():
	if not get_login():
		return requires_login()

	if request.method == "POST":
		if not csrf_match():
			return csrf_bail('key_add')
		for le_part in ('le-app', 'le-user', 'le-needs-hwid', 'le-active', 
						'le-expires', 'le-expires-select', 'le-expires-years',
						'le-expires-months', 'le-expires-weeks', 'le-expires-days', 'le-expires-hours',
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
		key_id = pysql_._cursor.lastrowid
		logger.info("Successfully created license", key_id)
		return redirect(url_for('key_edit', id=key_id))
	else:
		apps = []
		for app_ in pysql().get('apps'):
			app = {
				"id": app_['id'],
				"name": app_['name']
			}
			apps.append(Struct(**app))
		return render_template('keys.add.html', login=get_username(), apps=apps, csrf=csrf_make())

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
		if not csrf_match():
			return csrf_bail('key_edit', id=id)
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

		logger.info("Successfully updated license", id)

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
		"csrf": csrf_make()
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
		if not csrf_match():
			return csrf_bail('key_manage')
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
		"csrf": csrf_make()
	}
	return render_template('keys.remove.html', **extra)