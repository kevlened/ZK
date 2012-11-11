#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  zkp.py
#  
#  Copyright 2012 Christopher Carter <chris@gibsonsec.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		if sys.argv[1] in ('-i', '--install'):
			from zkpm.install import main
			main()
			sys.exit(0)
		elif sys.argv[1] in ('-v', '--version'):
			from zkpm.master import revision
			print 'ZK ',revision()
			sys.exit(0)
	
	try:
		from zkpm.master import main
	except ImportError as e:
		print 'An error occured importing ZK\'s master class.'
		print 'Try fixing your installation and try again.'
		raise
		sys.exit(1)
	main()
