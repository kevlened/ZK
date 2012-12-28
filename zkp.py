# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os, sys

no_daemon_key = 'start-no-daemon'
help_message = """python {script} [option] [flag] ...
Options and flags:
start \t\t: Start ZK and daemonize the process.
stop \t\t: Stop a running ZK process.
restart \t: Restart a running ZK process. (Calls stop() and start())
status \t\t: Check if a ZK daemon is currently running.
{non_daemon} : Start ZK without daemonizing. This runs in your current shell.

-i, --install \t: Setup the ZK environment. Run this after installing ZK.
-a, --add-user \t: Add a new administrator to your database.
-v, --version \t: Print the ZK revision and exit.
-h, --help \t: Display this help message and exit."""

try:
	# This script just checks if the user is using root.
	from zkpm.root_check import root_check
	root_check(no_daemon_key)
except ImportError as e:
	print 'Something went wrong importing root_check.'
	if os.getuid() == 0:
		print 'Sorry, but you can\'t run ZK as root.'
		sys.exit(2)
	raise

try:
	from zkpm.daemon import Daemon
except ImportError as e:
	print 'An error occured importing ZK\'s daemon class.'
	print 'Try fixing your installation and try again.'
	raise

class ZKDaemon(Daemon):
	def run(self):
		from zkpm.master import main
		main()

if __name__ == '__main__':
	_two = len(sys.argv) < 2
	if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
		print help_message.format(script=sys.argv[0], non_daemon=no_daemon_key)
		sys.exit(2 if _two else 0) # if they -h'd, we're good, otherwise it's borke.

	args = {
		"stdout": "/dev/null",
		"stderr": "/dev/null"
	}
	if no_daemon_key in sys.argv:
		# Set stdout and stderr flags to /dev/stdout for the daemon
		# this makes life easier for figuring out what's going on.
		args = {"stdout": "/dev/stdout", "stderr": "/dev/stderr"}

	daemon = ZKDaemon('/tmp/zk-daemon.pid', **args)
	for arg in sys.argv[1:]: # Obviously we don't want the name of the script
		arg = arg.lower()
		if arg in ('-i', '--install'):
			from zkpm.install import main as install_
			install_()
			sys.exit(0)
		
		elif arg in ('-a', '--add-user'):
			from zkpm.install import gather_details
			gather_details()
			print 'Your new user is now setup.'
			sys.exit(0)
		
		elif arg in ('-v', '--version'):
			from zkpm.master import revision
			print 'ZK', revision()
			print 'Free as in freedom.', 'https://github.com/PigBacon/ZK', '-', 'MIT Licensed'

		elif arg in ('start'):
			daemon.start()

		elif arg in ('start-no-daemon'):
			daemon.start(daemonize=False)

		elif arg in ('stop'):
			daemon.stop()

		elif arg in ('restart'):
			daemon.restart()

		elif arg in ('status'):
			if daemon.check():
				print 'ZK daemon currently running.'
			else:
				print 'ZK daemon not running.'
			sys.exit(0)
		
		elif arg in ('--explicity-use-root'):
			continue

		else:
			print 'Unknown argument', arg
			sys.exit(2)
