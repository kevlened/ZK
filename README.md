ZK (Protection)
==

What is it?
--
ZKP started off as a simple idea by PigBacon, which was mostly based around the management of Minecraft clients. This was private and - since it was written in PHP - came with high overhead, wasn't extremely well implemented, and was just a general unpleasant beast to work with.

Now it's a Python based management system which uses Flask as the front end for management, Twisted as the back end for communication, and SQLite for data storage.
This all rolls into one lovely bundle of joy.

What do I need to run it?
--
+ Python 2.6.6 (This is what I test with, 2.7.x should work, 3.x might)
+ [Twisted Python](http://twistedmatrix.com)
+ [Flask](http://flask.pocoo.org)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession)
+ sqlite3 (comes default in Python)

Installation
--
+ Download the latest version of ZK.
+ Install the dependencies
+ Open `default_settings.py` and, if required, change anything you feel.
+ Open a terminal where your `zkp.py` is.
+ Run the first time installer: `python zkp.py --install`
+ Follow the prompts and allow the database to be initialised and populated.
+ Run ZK: `python zkp.py`

Todo
--
+ Basically everything.

Status
--
+ (v0.0.1) Nonexistent
