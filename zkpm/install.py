# -*- coding: utf-8 -*-
from contextlib import closing
from zk_flask import connect_db, hash_pass
import default_settings as settings
import re, getpass, os, sys

def query_db(query, args=(), one=False, commit=False):
	db = connect_db()
	cur = db.execute(query, args)
	if commit:
		db.commit()
	rv = [dict((cur.description[idx][0], value) 
			for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv

def init_db():
	print 'Initialising database, and inserting schema.'
	with closing(connect_db()) as db:
		with open('zkpm{0}schema.sql'.format(os.sep), 'rb') as f:
			db.cursor().executescript(f.read())
		db.commit()
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
		print 'email: ',email
		correct = raw_input('Is this correct? [Y/n] ').lower() in ('y', 'yes')
	submit_details (username, password, email)

def submit_details(username, password, email):
	query = "INSERT INTO `users` (`username`, `password`, `email`) VALUES (?,?,?);"
	query_db(query, args=[u'{0}'.format(username), u'{0}'.format(hash_pass(username, password)), u'{0}'.format(email)], commit=True)

def main():
	if os.path.isfile(settings.DATABASE):
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
