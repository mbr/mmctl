#!/usr/bin/env python
# coding=utf8

from datetime import timedelta
from urlparse import urlparse

import Ice
#from jsonhack import jsonify
from flask import jsonify
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

def get_server_conf(meta, server, key):
    val = server.getConf(key)
    if '' == val:
        val = meta.getDefaultConf().get(key, '')
    return val

def get_server_port(meta, server):
    val = server.getConf('port')

    if '' == val:
        val = meta.getDefaultConf().get('port', 0)
        val = int(val) + server.id() - 1

    return int(val)

# create flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', connected_to='localhost:?????')

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
    return jsonify(returnValue=resuserssult)

@app.route('/api/list-servers/')
def api_list_servers():
    # compile list of servers
    servers = []

    for s in meta.getAllServers():
        servers.append({
            'id': s.id(),
            'name': get_server_conf(meta, s, 'registerName'),
            'address': '%s:%s' % (
                get_server_conf(meta, s, 'host'),
                get_server_port(meta, s),
            ),
            'running': s.isRunning(),
            'uptime': s.getUptime() if s.isRunning() else 0,
            'fuzzy_uptime': str(
                timedelta(seconds=s.getUptime()) if s.isRunning() else ''
            ),
            'users': (s.isRunning() and len(s.getUsers())) or 0,
            'maxusers': get_server_conf(meta, s, 'users') or 0
        });

    return jsonify(servers=servers)

@app.route('/api/create-server/', methods=('POST',))
def api_create_server():
    server = meta.newServer()

    return jsonify(server_id=server.id())

@app.route('/api/delete-server/', methods=('POST',))
def api_delete_server():
    server = meta.getServer(request.json['server_id'])

    if server.isRunning():
        server.stop()

    server.delete()

    return jsonify()

@app.route('/api/stop-server/', methods=('POST',))
def api_stop_server():
    server = meta.getServer(request.json['server_id'])
    server.stop();

    return jsonify()

@app.route('/api/start-server/', methods=('POST',))
def api_start_server():
    server = meta.getServer(request.json['server_id'])
    server.start();

    return jsonify()

if __name__ == '__main__':
    app.run(debug=True)
