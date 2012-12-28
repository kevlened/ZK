ZK
===

What is it?
---
ZK (which stands for _Zillion Keys_ (seriously, it does!)) started off as a simple idea by PigBacon, which was mostly based around the management of Minecraft clients. It was a private implementation written in PHP, and for some reason was highly sought after (only God may know why).

Now it's a Python based management system which uses Flask as the front end for management, Twisted as the back end for communication, and sqlite for data storage.
This rolls into one simplistic application and key management system for app developers and admins a-like.

It is developed by _Chris_ and _Huey_. It's licensed under the MIT License.

What do I need to run it?
---
+ Some __POSIX compliant__ operating system. (I test on Debian Wheezy)
	+ You could probably muck around to get it working on Windows, shouldn't be particularly hard.
	+ Windows isn't supported mainly because of the daemon system. I won't take any butchered commits so Windows works either, sorry.
+ Python 2.7.3 (This is what I test with, 2.6.x should work, 3.x probably won't)
+ [Twisted Python](http://twistedmatrix.com)
+ [Flask](http://flask.pocoo.org)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession)
+ sqlite3 (comes default in Python) or MySQL (requires MySQLdb Python module)
	+ You can choose either in the settings, so don't fret.
	+ sqlite3 is the default, so that should be fine.
+ [protobuf](http://code.google.com/p/protobuf/) (by google, whom we all love dearly)
	+ Try installing the `python-protobuf` package, if you're on a Debian based system.
	+ Otherwise, installation is simple, just check the protobuf site for more info.

Running
---
ZK is pretty simple to start/stop/restart and interact with.
+ Start: `python zkp.py start`
+ Stop: `python zkp.py stop`
+ Restart: `python zkp.py restart`
+ Start without daemonizing: `python zkp.py start-no-daemon`
	+ This means it will run in your current shell. (Exit with ^C)
	+ Good for debugging stuff in real time (otherwise just check debug log)
+ You can check the status of your daemon with: `python zkp.py status`
	+ This will only work if the server OS has a __/proc filesystem__.
	+ UNIX based OS's mostly do, I'm not certain about OSX, however.
	+ Since this is just for convenience, I won't change it to work on all OS types.
	+ You could alternatively use: `ps aux | grep -i python | grep -v grep` to check.

Logging
---
You are able to set a logging directory in your settings file. ZK will simply log into that directory, creating four files: `info.log`, `debug.log`, `warning.log`, `error.log`. The error.log will contain both errors and fatal errors (things which break ZK completely).
+ Even if you don't have DEBUG set to True in your settings, everything will still be written into the debug.log file. This means that if something goes wrong but you don't know what, you can still try and figure out what is was.
+ If something breaks, try and replicate it without daemonizing, (with DEBUG=True), and copy the error into an issue on GH.

Notes
---
+ This uses a modified version of my [pysql-wrapper](https://github.com/PigBacon/pysql-wrapper).
	+ The usage is the same, but it is modified to work with Flask.
	+ A pysql_wrapper object is closed every time a query is executed, so you should make a new one (simply `pysql()`) before querying stuff.
+ ZK __is not__ meant to prevent cracking.
	+ The weakest link in your app may well be the server, and whilst we'll try to prevent it being easy, this might well be a poor security system.
	+ This is aimed to make your life as a programmer/application manager easier, not be a foolproof anti-cracking protection system.
+ If you're interested in the database schema, look at the `schema_sqlite3.sql` file.
	+ `schema_mysql.sql` is three single line commands, because MySQL doesn't support `.executescript()` like sqlite. (Pah!)

Contributions
---
+ If you want to contribute, you should follow these rules:
	+ Tabs, __not__ spaces.
	+ UTF-8 files.
	+ All form fields should be prefixed with `le-`. (So we know what's form input, and to make people cringe)
	+ Var names should be `lowercase_with_underscores`
+ We're always interested in more examples for ZK client implementation.
	+ Feel free to write more in any language we're lacking.
	+ If you think you can improve one already here, feel free to pull it.

Installation
---
+ Download the latest version of ZK.
+ Install the dependencies
+ Open `settings.py` and, if required, change anything you feel.
	+ There is __lots__ which requires changing!
	+ Most paths are just simply `"/path/to/some_file"`, which you'll obviously have to change.
+ Open a terminal where your `zkp.py` is.
+ Run the first time installer: `python zkp.py --install`
+ Follow the prompts and allow the database to be initialised and populated.
+ Run ZK: `python zkp.py start`
	+ You should probably generate a secret key here.
	+ Visit http://host:port/secret and put those in your settings file, restart ZK.
+ You can stop ZK with: `python zkp.py stop`

Todo
---
+ Example clients in various languages to show implementation.
+ More robust logging. (__DONE__)
+ Fix some scetchy workaround hacks:
	+ HTML \<form\> + \<table\> hacks in `apps.edit.html` and `keys.edit.html`.
	+ MySQL schema + installing hacks. Probably not fixable, and not really a big issue.
+ Pagination for /app/manage and /key/manage. (Possibly just load more via JS)
+ Manage the wiki, explaining usage, modification, and implementation.
+ Complete implementation of the API.
+ STARTTLS and listen on one port instead of two, perhaps?

Status
---
### r7
+ ZK is now daemonised. This means it's easier to run.
	+ `python zkp.py start|stop|restart`
	+ `python zkp.py status` to check the status. (Requires procfs)
+ Examples are actually... there. Sort of.
+ Added checks so you can't run ZK as root. (os.getuid() == 0)
+ Images added to repo so I can put them on the wiki, or something.
+ Changed "le-shiggy-diggy" to "le-csrf", since it is infact a cross-site-request-forgery protection system. (I had just forgotten the name)
+ Cleaned up the installer a bit.
+ ZK has a nice command line documentation. `python zkp.py --help`

### r6
+ Twisted backend coming to life.
+ Python client example (very bare)

### r5
+ Cleaned up the code a lot.
+ Start of the API (useless, except for the JSON app and key list).
+ Flashed messages are now a lot easier to spot and they look a lot better.
+ You can now add extra admins easily with the `-a` or `--add-user` flag. e.g: `python zkp.py --add-user`
+ Expired keys will are checked and disabled every X seconds. Check times are changeable in the settings file.
	+ By default, the check is every __10 minutes__; this means a key could be active for up to 10 minutes more than it should be.
+ Start of Twisted backend (including ProtoBuf)

### r4
+ Key management now completely functional.
+ Added le-shiggy-diggy form security. This will stop cross site request attack attempts.
+ Added decent expiry system.
+ Made removing an app remove all attached licenses.

### r3
+ Functionality of site coming together.
+ App management now completely functional.
+ More logging, where applicable.
+ Flashed messages now fade away.
+ A bit more security.
+ Small fixes to the login system. (Will require change to any table schemas)

### r2
+ Changed to pysql-wrapper.
+ _Cleaned_ up the install function. (Required workarounds for MySQL, so it's not perfect.)
+ Support for MySQL aswell as default sqlite3.
+ Misc bits of code cleanup.
+ Start of `/manage/app` and `/manage/key` web pages. (Currently execute `abort(418)`.)

### r1
+ Front end mostly functional
+ Template works
+ Twisted backend is useless but functioning
+ KVSession is handling everything correctly and securely
