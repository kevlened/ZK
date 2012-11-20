# -*- coding: utf-8 -*-
import settings
	
def info(*args):
	print '[ INF ]',
	for arg in args:
		print arg,
	print ''

def debug(*args):
	if not settings.DEBUG:
		return
	print '[ DBG ]',
	for arg in args:
		print arg,
	print ''

def warning(*ags):
	print '[ WRN ]',
	for arg in args:
		print arg,
	print ''

def error(*args):
	print '[ ERR ]',
	for arg in args:
		print arg,
	print ''

def fatal(*args):
	print '[FATAL]',
	for arg in args:
		print arg,
	print ''