#!/usr/bin/env python
# coding=utf8

from urlparse import urlparse

import Ice
from jsonhack import jsonify
from flask import Flask, render_template, request

import commandline

args = commandline.parser.parse_args()

# for now, only command line arguments are our runtime configuration
rtconf = args

# load slice file, this could be done dynamicall later on
Ice.loadSlice(rtconf.slice_file)
import Murmur

ic = Ice.initialize()

server_url = urlparse(rtconf.server_url)
metaproxy = ic.stringToProxy(
    'Meta:tcp -h %s -p %d' % (server_url.hostname, server_url.port)
)
meta = Murmur.MetaPrx.checkedCast(metaproxy)
factories = {
    '::Murmur::Server': Murmur.ServerPrx,
}

# create flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/call/', methods=('POST',))
def api_meta():
    args = request.json['args'] or []
    target = request.json['target']

    if 'meta' == target:
        target_obj = meta
    else:
        # gotta find the target through ice first
        prx = ic.stringToProxy(target)

        target_obj = factories[prx.ice_id()].checkedCast(prx)

    method = getattr(target_obj,
                     request.json['method_name'])

    result = method(*args)
    return jsonify(returnValue=result)

if __name__ == '__main__':
    app.run(debug=True)
