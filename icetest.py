#!/usr/bin/env python
# coding=utf8

from math import ceil
from datetime import timedelta, datetime
from urlparse import urlparse

import Ice
#from jsonhack import jsonify
from flask import jsonify, url_for
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

SERVER_LOG_PAGER_PER_PAGE = 10


class ClientPager(object):
    def __init__(self,
                 endpoint,
                 page=1,
                 per_page=10,
                 total_count=None,
                 pager_size=6,
                 **kwargs):
        self.endpoint = endpoint
        self.endpoint_args = kwargs
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.pager_size = pager_size

    @property
    def total_pages(self):
        if None != self.total_count:
            return int(ceil(self.total_count/float(per_page)))

    def toJSONDict(self):
        pager = {}
        pages = []

        if not self.total_count:
            pager['prev'] = None if -1 == self.page else self.page-1
            pager['next'] = self.page+1
            pages.append(1)

            if self.page > self.pager_size-1:
                pages.append('...')
                pages += range(self.page-self.pager_size+4, self.page+1)
                pages.append('...')
            else:
                pages += range(2, self.page+1)
                pages.append('...')

        pager['total_count'] = self.total_count
        pager['per_page'] = self.per_page
        pager['page'] =  self.page
        pager['pages'] = pages

        return pager


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
    return render_template('index.html', version=meta.getVersion()[3])


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


@app.route('/api/get-global-config/')
def api_get_global_config():
    conf = meta.getDefaultConf()

    return jsonify(globalConf = conf)


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


@app.route('/api/get-server-config/<int:server_id>/')
def api_get_server_config(server_id):
    server = meta.getServer(server_id)

    return jsonify(
        serverId = server.id(),
        isRunning = server.isRunning(),
        config = server.getAllConf(),
        uptime = server.getUptime() if server.isRunning() else 0,
        fuzzyUptime = str(
            timedelta(seconds=server.getUptime()) if server.isRunning() else ''
        ),
    )


@app.route('/api/get-server-log/<int:server_id>/')
@app.route('/api/get-server-log/<int:server_id>/<int:page>/')
def api_get_server_log(server_id, page):
    server = meta.getServer(server_id)
    log_entries = []

    # Murmur documentation bug:
    # getLog doesn't take (first, last) arguments, but rather
    # first, amount
    for l in server.getLog((page-1)*SERVER_LOG_PAGER_PER_PAGE,
                           SERVER_LOG_PAGER_PER_PAGE):
        timestamp = datetime.utcfromtimestamp(int(l.timestamp))
        log_entries.append((
            l.timestamp,
            l.txt,
            timestamp.strftime('%A, %d. %B %Y at %H:%M:%S'),
            timestamp.strftime('%H:%M:%S'),
        ))

    return jsonify(
        logEntries = log_entries,
        pager = ClientPager('api_get_server_log', page, server_id=server_id).
                toJSONDict()
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
