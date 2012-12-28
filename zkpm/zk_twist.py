# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from proto import ZKM_pb2, ZKReply_pb2
import settings
from zk_flask import pysql
import logger

import hashlib
import time

class ZKConst:
	get = {
		'BAIL': (-1, 'Something went wrong, bail!'),
		'SUCCESS': (0, 'Successfully authenticated.'),
		'INVALID_HWID': (1, 'Invalid HWID provided.'),
		'DISABLED': (2, 'This key is disabled.'),
		'EXPIRED': (3, 'This key has expired.'),
		'NO_SUCH_KEY': (4, 'That key does not exist.')
	}

class ZKProtocol(Protocol):

	def __init__(self, factory):
		self.factory = factory
		self.closed = False
		self.stamp = int(time.time())

	def connectionMade(self):
		self.ip, self.port = self.transport.getPeer().host, self.transport.getPeer().port
		logger.info("Connection from {0}:{1}".format(self.ip, self.port))
		self.factory.clients.append(self)

	def dataReceived(self, data):
		try:
			zkm = ZKM_pb2.ZKM()
			zkm.ParseFromString(data)
			key = pysql().where('key', zkm.key).get('licenses')
			if len(key) != 1:
				logger.info("{0}/{1}: supplied invalid license.".format(self.ip, zkm.key))
				zkreply = ZKReply_pb2.ZKReply()
				zkreply.reply, zkreply.reply_str = ZKConst.get['NO_SUCH_KEY']
				zkreply.key = zkm.key
				zkreply.user = ""
				zkreply.app = ""
				self.send(zkreply.SerializeToString(), raw=True)
				self.close()
				return
			key = key[0]

			if key['hwid'] == "":
				# Update the HWID if we're missing one.
				pysql().where('id', key['id']).update('licenses', {"hwid": zkm.hwid})
				key['hwid'] = zkm.hwid

			if int(key['expires']) == -1:
				logger.info("{0}/{1}: requested auth for expired license.".format(self.ip, zkm.key))
				zkreply = ZKReply_pb2.ZKReply()
				zkreply.reply, zkreply.reply_str = ZKConst.get['EXPIRED']
				zkreply.key = zkm.key
				zkreply.user = key['user']
				app = pysql().where('id', key['app']).get('apps')
				zkreply.app = app[0]['name'] if app else ''
				self.send(zkreply.SerializeToString(), raw=True)
				self.close()
				return

			if bool(key['disabled']):
				logger.info("{0}/{1}: requested auth for disabled license.".format(self.ip, zkm.key))
				zkreply = ZKReply_pb2.ZKReply()
				zkreply.reply, zkreply.reply_str = ZKConst.get['DISABLED']
				zkreply.key = zkm.key
				zkreply.user = key['user']
				app = pysql().where('id', key['app']).get('apps')
				zkreply.app = app[0]['name'] if app else ''
				self.send(zkreply.SerializeToString(), raw=True)
				self.close()
				return

			if bool(key['needs_hwid']) and key['hwid'] != zkm.hwid:
				logger.info("{0}/{1}: supplied invalid HWID.".format(self.ip, zkm.key))
				logger.debug("{0} provided, {1} needed.".format(zkm.hwid, key['hwid']))
				zkreply = ZKReply_pb2.ZKReply()
				zkreply.reply, zkreply.reply_str = ZKConst.get['INVALID_HWID']
				zkreply.key = zkm.key
				zkreply.user = key['user']
				app = pysql().where('id', key['app']).get('apps')
				zkreply.app = app[0]['name'] if app else ''
				self.send(zkreply.SerializeToString(), raw=True)
				self.close()
				return

			logger.info("{0}/{1}: successfully authenticated.".format(self.ip, zkm.key))
			zkreply = ZKReply_pb2.ZKReply()
			zkreply.reply, zkreply.reply_str = ZKConst.get['SUCCESS']
			zkreply.key = zkm.key
			zkreply.user = key['user']
			app = pysql().where('id', key['app']).get('apps')
			zkreply.app = app[0]['name'] if app else ''
			self.send(zkreply.SerializeToString(), raw=True)
			#self.close()
			return

		except Exception as e:
			zkreply = ZKReply_pb2.ZKReply()
			zkreply.reply, zkreply.reply_str = ZKConst.get['BAIL']
			zkreply.key = ""
			zkreply.user = ""
			zkreply.app = ""
			self.send(zkreply.SerializeToString(), raw=True)
			self.close()
			return

	def connectionLost(self, reason):
		logger.info("Client connection {0}:{1} {2}.".format(self.ip, self.port, 'closed' if self.closed else 'disconnected'))
		if self in self.factory.clients:
			self.factory.clients.remove(self)

	def send(self, data, raw=False):
		if not raw:
			data = str(data)
		self.transport.write(data)

	def close(self, force=False):
		logger.debug("Close called:",force)
		if self.closed:
			logger.debug("Closing already closed client {0}:{1}".format(self.ip, self.port))
			return
		self.closed = True
		if force:
			self.transport.abortConnection()
		else:
			self.transport.loseConnection()
		if self in self.factory.clients:
			self.factory.clients.remove(self)

class ZKFactory(Factory):
	def __init__(self):
		self.clients = []
		self.check()

	def check(self):
		# logger.debug() calls are commented, so that
		# we don't spam the log files with junk.
		
		#logger.debug("Checking for worthless connections.")
		worthless = 0
		stamp = int(time.time())
		for client in self.clients:
			if (stamp - client.stamp) >= settings.TWIST_TIMEOUT:
				client.close(True)
				worthless += 1
		#logger.debug("Found", worthless, "worthless connections. Waiting for", settings.TWIST_TIMEOUT_CHECK, "seconds.")
		reactor.callLater(settings.TWIST_TIMEOUT_CHECK, self.check)

	def buildProtocol(self, addr):
			return ZKProtocol(self)