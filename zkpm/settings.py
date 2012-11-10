# -*- coding: utf-8 -*-
# Disable this in a production environment.
# This enables Flask's debugger.
DEBUG = True

# --- Webserver Settings ---
# The port and host which the web front will bind to.
WEB_HOST = "127.0.0.1"
WEB_PORT = "8080"
# Should we shrink the css/js/html?
WEB_SHRINK = False

# --- ZK Server Settings ---
# The port and host which the ZK server replies on.
ZK_HOST = "127.0.0.1"
ZK_PORT = "1111"

# --- Database Settings ---
# Can be sqlite3 or MySQL
DATABASE_TYPE = 'mysql' #"sqlite3"
# These are only needed if you picked MySQL above.
DATABASE_HOST = "localhost"
DATABASE_USER = "foo"
DATABASE_PASS = "baz"
DATABASE_NAME = "test"

# If you're using sqlite, give us a database file to work with.
DATABASE_PATH = "zk.db"

# --- Secret Settings ---

# This should be a random and long string of characters.
# Keep this secret, it's used for signing the authentication parts.
# To generate a secret key, you can run ZK and visit /secret, or /secret/<length>.
SECRET_KEY = "something_secret_and_hard_to_guess"

# This should be never change once you setup ZK.
# If you do, passwords will require a reset.
PASSWORD_SALT = "something_long_and_secret_ok?"
