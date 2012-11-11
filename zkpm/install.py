# -*- coding: utf-8 -*-
from contextlib import closing
from zk_flask import pysql as pysql_
from zk_flask import hash_pass
import settings
import re, getpass, os, sys

def init_db():
	print 'Initialising database, and inserting schema.'
	schema = False
	if settings.DATABASE_TYPE.lower() in ('sqlite', 'sqlite3'):
		schema = 'schema_sqlite3.sql'
		db_t = 'sqlite'
	elif settings.DATABASE_TYPE.lower() in ('mysql'):
		schema = 'schema_mysql.sql'
		db_t = 'mysql'
	if not schema:
		print 'Given database type was not valid, bailing.'
		sys.exit(1)
	pysql = pysql_()

	# Stupid workarounds because MySQL doesn't support .executescript()
	if db_t == 'sqlite':
		with open('zkpm{0}{1}'.format(os.sep, schema), 'rb') as f:
			pysql._cursor.executescript(f.read())
			pysql._dbc.commit()
	elif db_t == 'mysql':
		with open('zkpm{0}{1}'.format(os.sep, schema), 'rb') as f:
			for line in f.readlines():
				print line
				pysql = pysql_()
				pysql.query(line)
	print 'Database initialised.'

def gather_details():
	print 'We will now setup your initial admin user.'
	correct = False
	username, password, password1, email = ('','',' ','')
	while not correct:
		username = raw_input('Admin username: ')
		while password != password1:
			password = getpass.getpass()
			password1 = getpass.getpass('Password again: ')
			if password != password1:
				print 'Passwords do not match, try again.'
			else:
				break
		email = raw_input('Your email (optional): ')
		print 'User: ',username
		print 'email:',email
		correct = raw_input('Is this correct? [Y/n] ').lower() in ('y', 'yes')
	submit_details (username, password, email)

def submit_details(username, password, email):
	pysql = pysql_()
	data = {
		"login": username.lower(),
		"username": username,
		"password": hash_pass(username, password),
		"email": email
	}
	pysql.insert('users', data)

def main():
	if settings.DATABASE_TYPE.lower() in ('sqlite', 'sqlite3') and os.path.isfile(settings.DATABASE_PATH):
		print 'Sorry, it appears the ZK database you\'ve selected already exists.'
		print 'Either delete your database file, or change it to a different file in the settings file.'
		sys.exit(1)
	print 'Welcome to the ZK installation steps. Press Ctrl-C to exit.'
	try:
		init_db()
		gather_details()
	except KeyboardInterrupt as e:
		print 'Exiting!'
		sys.exit(0)
	print '-'*40
	print 'Installation is now complete!'
	print 'Feel free to run ZK now.'
