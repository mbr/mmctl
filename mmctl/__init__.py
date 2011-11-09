#!/usr/bin/env python
# coding=utf8

from urlparse import urlparse

import Ice
from flask import Flask
from flaskext.assets import Environment as AssetEnvironment, Bundle

import defaults

def create_app(configfile='mmctl.conf'):
    app = Flask(__name__)
    app.version = '0.2.0'
    app.config.from_object(defaults)

    try:
        app.config.from_pyfile(configfile)
    except IOError:
        # load configuration blueprint
        from cfgutil import cfgutil
        import random
        app.register_blueprint(cfgutil)

        # generate initial salt

        # 64 bit recommended, let's do a bit more
        app.initial_salt = '%x' % random.SystemRandom().getrandbits(96)

        app.initial_iterations = 2000 #  seems a good compromise
        #app.initial_iterations = 20 #  makes debugging more fun
        app.initial_keylength = 64
    else:
        # load api/ui blueprint
        from mmctlui import mmctlui
        app.register_blueprint(mmctlui)

        # load slice file, this could be done dynamicall later on
        Ice.loadSlice(app.config['SLICE_FILE'])
        import Murmur

        ic = Ice.initialize()

        metaproxy = ic.stringToProxy(app.config['ICE_STRING'])
        app.meta = Murmur.MetaPrx.checkedCast(metaproxy)

    # check if there is a configuration file, if not, run config blueprint
    AssetEnvironment(app)

    return app
