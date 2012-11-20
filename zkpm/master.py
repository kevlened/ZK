# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

import settings
import zk_flask # Setup the Flask app + frontend handle.
import zk_app
import zk_key
import zk_twist
import api
import logger

zk_factory = zk_twist.ZKFactory()
reactor.listenTCP(int(settings.ZK_PORT), zk_factory)
resource = WSGIResource(reactor, reactor.getThreadPool(), zk_flask.app)
site = Site(resource)
reactor.listenTCP(int(settings.WEB_PORT), site)

def main():
	logger.info('Setting up ZK flask app.')
	zk_flask.main(api.app)
	logger.info('Running reactor.')
	reactor.run()

def revision():
	return 'r5-git'
