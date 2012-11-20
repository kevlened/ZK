# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

import settings, logger, util
import zk_flask as zk
from zk_flask import languages, get_login, requires_login, pysql, Struct
from zk_flask import get_username, shiggy_make, shiggy_match, shiggy_bail

import re

app = zk.app

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
		if not re.match(r'^[a-zA-Z0-9_\-]+$', le_name):
			flash("Sorry, app names can only include alphanumeric characters, dashes and underscores.", 'error')
			return redirect(url_for('app_add'))

		le_language = request.form['le-language'][:32]
		if le_language == "Other":
			le_language = request.form['le-other-language'][:32] # If they specify Other, grab le-other-language.
		if not re.match(r'^[a-zA-Z0-9_\-#+\.]+$', le_language):
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
			if not re.match(r'^[a-zA-Z0-9_\-]+$', le_name):
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
			if not re.match(r'^[a-zA-Z0-9_\-#+\.]+$', language):
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
		licenses = pysql().where('app', id).get('licenses')
		if len(licenses) > 0 and not pysql().where('app', id).delete('licenses'):
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