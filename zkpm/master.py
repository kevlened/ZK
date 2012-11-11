# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
import settings
import zk_flask # Setup the Flask app + frontend handle.
import logger

class ZKProtocol(Protocol):

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.ip, self.port = self.transport.getPeer().host, self.transport.getPeer().port
		logger.info("Connection from {0}:{1}".format(self.ip, self.port))
		self.factory.clients.append(self)

	def dataReceived(self, data):
		print data

	def connectionLost(self, reason):
		logger.info("Client {0}:{1} disconnected ({2})".format(self.ip, self.port, reason))
		self.factory.clients.remove(self)

class ZKFactory(Factory):
	def __init__(self):
		self.clients = []

	def buildProtocol(self, addr):
			return ZKProtocol(self)


zk_factory = ZKFactory()
reactor.listenTCP(int(settings.ZK_PORT), zk_factory)
resource = WSGIResource(reactor, reactor.getThreadPool(), zk_flask.app)
site = Site(resource)
reactor.listenTCP(int(settings.WEB_PORT), site)

def main():
	logger.info('Running reactor.')
	reactor.run()

def revision():
	return 'r3'
