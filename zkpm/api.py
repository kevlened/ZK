# -*- coding: utf-8 -*-
from flask import Blueprint, Flask, render_template, session, abort, request
from flask import g, redirect, url_for, flash, make_response, jsonify

import zk_flask as zk
from zk_flask import pysql, hash_pass

app = Blueprint('api', __name__, template_folder='templates')

def api_validate():
	if not zk.get_login() and not zk.get_http_login():
		resp = jsonify({"error": "Not authenticated", "error-num": 1})
		resp.status_code = 401
		return resp
	if zk.get_http_login():
		pass_ = hash_pass(request.authorization.username, request.authorization.password)
		users = pysql().where('login', request.authorization.username.lower()).where('password', pass_).get('users')
		if len(users) != 1:
			resp = jsonify({"error": "Authication invalid", "error-num": 2})
			resp.status_code = 401
			return resp
	return None

def user():
	"""Return a username of the current API user.
		If they're logged into the site, return the username,
		If they're not, return the HTTP authorization username.
	"""
	return request.authorization.username if zk.get_http_login() else zk.get_username()

### API front facing functions below.

@app.route("/")
def api_root():
	return redirect(url_for('index'))

@app.route("/app.json")
def api_app_json():
	validate = api_validate()
	if validate is not None:
		return validate

	apps_pulled = pysql().get('apps')
	apps = []
	for app in apps_pulled:
		app['users'] = len(pysql().where('id', app['id']).get('licenses'))
		apps.append(app)
	data = {
		"user": user(),
		"apps": apps
	}
	return jsonify(data)

@app.route("/keys.json")
def api_keys_json():
	validate = api_validate()
	if validate is not None:
		return validate

	keys_pulled = pysql().get('licenses')
	keys = []
	for key in keys_pulled:
		app = pysql().where('id', key['app']).get('apps')
		if len(app) != 1:
			continue
		key['app.name'] = app[0]['name']
		keys.append(key)
	data = {
		"user": user(),
		"keys": keys
	}
	return jsonify(data)