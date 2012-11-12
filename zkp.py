#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		if sys.argv[1] in ('-i', '--install'):
			from zkpm.install import main
			main()
			sys.exit(0)
		elif sys.argv[1] in ('-v', '--version'):
			from zkpm.master import revision
			print 'ZK', revision()
			print 'Free as in freedom:', 'https://github.com/PigBacon/ZK'
			sys.exit(0)
	
	try:
		from zkpm.master import main
	except ImportError as e:
		print 'An error occured importing ZK\'s master class.'
		print 'Try fixing your installation and try again.'
		raise
		sys.exit(1)
	main()
