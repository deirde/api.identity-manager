#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cherrypy import wsgiserver

from app import app
from app.config.Config import Config as config_app

###
# The app runner.
###
if config_app().data['debug'] and config_app().data['testing']:
    app.run(
        config_app().data['ip'],
        port=config_app().data['port']
    )

###
# With the flags debug and testing on false
#   the app is considered running in production mode and a different server is used.
###
else:
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(
        (config_app().data['ip'], config_app().data['port']), d)
    server.start()
