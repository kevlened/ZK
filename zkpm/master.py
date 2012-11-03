# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
import default_settings as settings
import zk_flask # Setup the Flask app + frontend handle.

class Logger():
	def info(self, *args):
		Logger.info(args)
	
	@staticmethod
	def info(*args):
		print '[INFO]',
		for arg in args:
			print arg,
		print ''

class ZKProtocol(Protocol):

	def __init__(self, factory):
		self.factory = factory
		self.logger = Logger()

	def connectionMade(self):
		self.ip, self.port = self.transport.getPeer().host, self.transport.getPeer().port
		self.logger.info("Connection from {0}:{1}".format(self.ip, self.port))
		self.factory.clients.append(self)

	def dataReceived(self, data):
		print data

	def connectionLost(self, reason):
		self.logger.info("Client {0}:{1} disconnected ({2})".format(self.ip, self.port, reason))
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
	Logger.info('Running reactor.')
	reactor.run()
