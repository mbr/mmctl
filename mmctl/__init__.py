#!/usr/bin/env python
# coding=utf8

import os
from urlparse import urlparse

from flask import Flask
from flaskext.assets import Environment as AssetEnvironment, Bundle

import defaults
from utils import load_meta

def create_app(configfile='mmctl.conf'):
    app = Flask(__name__)
    app.version = '0.2.0'
    app.config.from_object(defaults)

    try:
        conffile = os.path.join(app.instance_path, 'mmctl.conf')
        app.config.from_pyfile(conffile)
    except IOError:
        # load configuration blueprint
        from cfgutil import cfgutil
        import random
        app.register_blueprint(cfgutil)

        # generate initial salt
        if None == app.config['PBKDF2_SALT']:
            app.config['PBKDF2_SALT'] = \
                '%x' % random.SystemRandom().getrandbits(96)
    else:
        # load api/ui blueprint
        from mmctlui import mmctlui
        app.register_blueprint(mmctlui)

        # load slice file, this could be done dynamicall later on
        app.meta = load_meta(app, app.config['ICE_STRING'])

    # check if there is a configuration file, if not, run config blueprint
    AssetEnvironment(app)

    return app
