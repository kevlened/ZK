# -*- coding: utf-8 -*-
def guess_hash(hashed):
	"""Attempt to guess the hash type from a hashed string.
		Simply checks the length of the string, for the known common hashes.
		Can guess md5, sha1, sha224, sha256, sha384, sha512. (all from python's hashlib)
	"""
	hlen = len(hashed)
	if hlen == 32:
		return 'md5'
	elif hlen == 40:
		return 'sha1'
	elif hlen == 56:
		return 'sha224'
	elif hlen == 64:
		return 'sha256'
	elif hlen == 96:
		return 'sha384'
	elif hlen == 128:
		return 'sha512'
	return False

def timestamp_from_str(str_):
	"""Return a UNIX timestamp in the future after parsing how much to add.

		The string should be something like 1y2m3w4d5h,
		specifying years, months, weeks, days, accordingly.
		If something isn't wanted, it should still be there,
		but the number should be a 0.
	"""
	import re, time
	pattern = r'(?:(?P<years>\d+)y)?(?:(?P<months>\d+)m)?(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?'
	reg = re.compile(pattern)
	if not reg.match(str_):
		return 0
	result = reg.match(str_).groupdict()
	timestamp = int(time.time())
	timestamp_ = timestamp
	def add(h, t, s):
		for x in range(int(h)):
			s += t
		return s
	timestamp = add(result['hours'], 60 * 60, timestamp)
	timestamp = add(result['days'], 60 * 60 * 24, timestamp)
	timestamp = add(result['weeks'], 60 * 60 * 24 * 7, timestamp)
	timestamp = add(result['months'], 60 * 60 * 24 * 7 * 4, timestamp)
	timestamp = add(result['years'], 60 * 60 * 24 * 7 * 4 * 12, timestamp)
	return timestamp

def expires_str(stamp):
	"""Somewhat hacky method to turn a timestamp into a nicely formatted string.

		Could be significantly cleaned up if dictionaries stayed in order.
	"""
	if stamp == 0:
		return 'Never'
	from datetime import datetime, timedelta
	import time
	diff = (datetime.fromtimestamp(stamp) - datetime.now())
	secs = diff.seconds
	if diff.days > 0:
		secs += ((60 * 60 * 24) * (diff.days - 1))
	units = [
		(604800 * 4 * 12),
		(604800 * 4),
		604800,
		86400,
		3600,
		60,
		1
		]
	units_ = [
		'year',
		'month',
		'week',
		'day',
		'hour',
		'min',
		'sec'
		]
	out = []
	has_hours, is_ms = (False, False)
	for k,v in enumerate(units):
		if secs < v:
			continue
		num = secs / v
		secs = secs % v
		s = '' if num == 1 else 's'
		if num == 0:
			continue
		if k < (len(units_) - 3):
			has_hours = True
		if k >= (len(units_) - 2):
			is_ms = True
		if has_hours and is_ms:
			continue
		out.append('{} {}{}'.format(num, units_[k], s))
	return ', '.join(out)

def expires_dict(stamp):
	"""Somewhat hacky method to turn a timestamp into a dict of expiration values.

		Could be significantly cleaned up if dictionaries stayed in order.
	"""
	if stamp == 0:
		return {
			'years': 0,
			'months': 0,
			'weeks': 0,
			'days': 0,
			'hours': 0
		}
	from datetime import datetime, timedelta
	import time
	diff = (datetime.fromtimestamp(stamp) - datetime.now())
	secs = diff.seconds
	if diff.days > 0:
		secs += ((60 * 60 * 24) * (diff.days - 1))
	units = [
		(604800 * 4 * 12),
		(604800 * 4),
		604800,
		86400,
		3600
		]
	units_ = [
		'years',
		'months',
		'weeks',
		'days',
		'hours'
		]
	out = {
		'years': 0,
		'months': 0,
		'weeks': 0,
		'days': 0,
		'hours': 0
	}
	for k,v in enumerate(units):
		if secs < v:
			continue
		num = secs / v
		secs = secs % v
		out[units_[k]] = num
	return out

def key_from_style(style=1, app=""):
	out = ""
	key = []
	import random, string, re
	if not isinstance(style, int):
		try:
			style = int(style)
		except ValueError as e:
			style == 1
	if style == 3:
		for x in range(4):
			bits = string.ascii_uppercase + string.digits
			key.append(''.join(random.choice(bits) for x in range(4)))
		out = ''.join(key)
	elif style == 2:
		clean_app = re.sub('[^a-zA-Z0-9]', '', app)
		key.append(clean_app[:5])
		for x in range(4):
			bits = string.ascii_uppercase + string.digits
			key.append(''.join(random.choice(bits) for x in range(4)))
		out = '-'.join(key)
	else: #style == 1
		for x in range(4):
			bits = string.ascii_uppercase + string.digits
			key.append(''.join(random.choice(bits) for x in range(4)))
		out = '-'.join(key)
	return out[:64] # Trim if needed.
