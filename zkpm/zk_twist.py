# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from zkpm.proto import ZKM_pb2

class ZKProtocol(Protocol):

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.ip, self.port = self.transport.getPeer().host, self.transport.getPeer().port
		logger.info("Connection from {0}:{1}".format(self.ip, self.port))
		self.factory.clients.append(self)

	def dataReceived(self, data):
		try:
			zkm = ZKM_pb2.ZKM()
			zkm = ZKM_pb2.ParseFromString(data)
			print zkm
			print zkm.key(), zkm.hwid(), zkm.type(), zkm.options()
		except Exception as e:
			raise

	def connectionLost(self, reason):
		logger.info("Client {0}:{1} disconnected ({2})".format(self.ip, self.port, reason))
		self.factory.clients.remove(self)

class ZKFactory(Factory):
	def __init__(self):
		self.clients = []

	def buildProtocol(self, addr):
			return ZKProtocol(self)