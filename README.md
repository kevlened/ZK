ZK (Protection)
==

What is it?
--
ZKP started off as a simple idea by PigBacon, which was mostly based around the management of Minecraft clients. This was private and - since it was written in PHP - came with high overhead, wasn't extremely well implemented, and was just a general unpleasant beast to work with.

Now it's a Python based management system which uses Flask as the front end for management, Twisted as the back end for communication, and SQLite for data storage.
This all rolls into one lovely bundle of joy.

What do I need to run it?
--
+ Python 2.7 (This is what I test with, it may work with higher or lower versions)
+ [Twisted Python](http://twistedmatrix.com)
+ [Flask](http://flask.pocoo.org)
+ SQLite (comes default in Python)
