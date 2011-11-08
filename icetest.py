#!/usr/bin/env python
# coding=utf8

from urlparse import urlparse

import Ice
from flask import Flask
from flaskext.assets import Environment as AssetEnvironment, Bundle

import defaults

def create_app(configfile='mmctl.conf'):
    app = Flask(__name__)
    app.config.from_object(defaults)

    try:
        app.config.from_pyfile(configfile)
    except IOError:
        # load configuration blueprint
        from cfgutil import cfgutil
        app.register_blueprint(cfgutil)
    else:
        # load api/ui blueprint
        from mmctlui import mmctlui
        app.register_blueprint(mmctlui)

        # load slice file, this could be done dynamicall later on
        Ice.loadSlice(app.config['SLICE_FILE'])
        import Murmur

        ic = Ice.initialize()

        app.server_url = urlparse(app.config['SERVER_URL'])
        metaproxy = ic.stringToProxy(
            'Meta:tcp -h %s -p %d' % (app.server_url.hostname,
                                      app.server_url.port)
        )
        app.meta = Murmur.MetaPrx.checkedCast(metaproxy)

    # check if there is a configuration file, if not, run config blueprint
    AssetEnvironment(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
