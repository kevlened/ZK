# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, ssl
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

import settings
import zk_flask # Setup the Flask app + frontend handle.
import zk_app
import zk_key
import zk_twist
import zk_api
import logger

zk_factory = zk_twist.ZKFactory()
ssl_context = ssl.DefaultOpenSSLContextFactory(
	settings.KEY_PRIV,
	settings.KEY_PUB
)
# We listen on 1111 (def.) for non-ssl connections,
# and 1112 (def.) for SSL connections.
# You can connect to either, depending on availability of SSL.
reactor.listenTCP(int(settings.ZK_PORT), zk_factory)
reactor.listenSSL(int(settings.ZK_PORT_SSL), zk_factory, contextFactory=ssl_context)
resource = WSGIResource(reactor, reactor.getThreadPool(), zk_flask.app)
site = Site(resource)
reactor.listenTCP(int(settings.WEB_PORT), site)

def main():
	logger.info('Setting up ZK frontend. ({0})'.format(revision()))
	zk_flask.main(api_app=zk_api.app, revision_=revision)
	logger.info('Running reactor.')
	reactor.run()

def revision():
	return 'r7-git'
