ZK (Protection)
==

What is it?
--
ZK(P) started off as a simple idea by PigBacon, which was mostly based around the management of Minecraft clients. This was private and - since it was written in PHP - came with high overhead, wasn't extremely well implemented, and was just a general unpleasant beast to work with.

Now it's a Python based management system which uses Flask as the front end for management, Twisted as the back end for communication, and sqlite for data storage.
This all rolls into one lovely bundle of joy.

It is developed by _Chris_ and _Huey_.

What do I need to run it?
--
+ Python 2.7.3 (This is what I test with, 2.6.x should work, 3.x probably won't)
+ [Twisted Python](http://twistedmatrix.com)
+ [Flask](http://flask.pocoo.org)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession)
+ sqlite3 (comes default in Python) or MySQL (requires MySQLdb Python module)
	+ You can choose either in the settings, so don't fret.
	+ sqlite3 is the default, so that should be fine.

Notes
--
+ This uses a modified version of my [pysql-wrapper](https://github.com/PigBacon/pysql-wrapper).
	+ The usage is the same, but it is modified to work with the multiple threading ideas of Flask.
	+ A pysql_wrapper object is closed every time a query is executed, so you should make a new one before querying stuff.
+ ZK __is not__ meant to prevent cracking.
	+ The weakest link in your app may well be the server, and whilst we'll try to prevent it being easy, this might well be a poor security system.
	+ This is aimed to make your life as a programmer/application manager easier, not be a foolproof anti-cracking protection system.
+ If you're interested in the database schema, look at the `schema_sqlite3.sql` file.
	+ `schema_mysql.sql` is three single line commands, because MySQL doesn't support `.executescript()` like sqlite. (Pah!)

Contributions
--
+ If you want to contribute, you should follow these rules:
	+ Tabs, __not__ spaces.
	+ UTF-8 files.
	+ All form fields should be prefixed with `le-`. (So we know what's form input, and to make people cringe)
	+ Var names should be `lowercase_with_underscores`
+ We're always interested in more examples for ZK client implementation.
	+ Feel free to write more in any language we're lacking.
	+ If you think you can improve one already here, feel free to pull it.

Installation
--
+ Download the latest version of ZK.
+ Install the dependencies
+ Open `settings.py` and, if required, change anything you feel.
+ Open a terminal where your `zkp.py` is.
+ Run the first time installer: `python zkp.py --install`
+ Follow the prompts and allow the database to be initialised and populated.
+ Run ZK: `python zkp.py`
	+ You should probably generate a secret key here.
	+ Visit http://yourhost:port/secret and put those in your settings file, restart ZK.

Todo
--
+ Complete front end management.
+ Backend + backend protocol.
+ Example clients in various languages to show implementation.
+ More robust logging.
+ Fix some scetchy workaround hacks:
	+ HTML \<form\> + \<table\> hacks in `templates/apps.edit.html`.
	+ MySQL schema + installing hacks. Probably not fixable, and not really a big issue.

Status
--
+ __r3__
	+ Functionality of site coming together.
	+ App management now completely functional.
	+ More logging, where applicable.
	+ Flashed messages now fade away.
	+ A bit more security.
	+ Small fixes to the login system. (Will require change to any table schemas)
+ __r2__
	+ Changed to pysql-wrapper.
	+ _Cleaned_ up the install function. (Required workarounds for MySQL, so it's not perfect.)
	+ Support for MySQL aswell as default sqlite3.
	+ Misc bits of code cleanup.
	+ Start of `/manage/app` and `/manage/key` web pages. (Currently execute `abort(418)`.)
+ __r1__
	+ Front end mostly functional
	+ Template works
	+ Twisted backend is useless but functioning
	+ KVSession is handling everything correctly and securely
