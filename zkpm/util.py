# -*- coding: utf-8 -*-
def guess_hash(hashed):
	'''Attempt to guess the hash type from a hashed string.
		Simply checks the length of the string, for the known common hashes.
		Can guess md5, sha1, sha224, sha256, sha384, sha512. (all from python's hashlib)
	'''
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
