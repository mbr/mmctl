#!/usr/bin/env python
# coding=utf8

from datetime import timedelta, datetime

from flask import Blueprint, jsonify, url_for, render_template, request,\
                  current_app

from ..utils import *

mmctlui = Blueprint('mmctlui', __name__,
                    template_folder='templates',
                    static_folder='static')

@mmctlui.route('/')
@require_auth('mmctlui.login')
def index():
    return render_template('index.html',
                           version=current_app.meta.getVersion()[3])


@mmctlui.route('/login/')
def login():
    return render_template(
        'login.html',
        follow_up=url_for('mmctlui.index', _external=True)
    )


@mmctlui.route('/api/list-servers/')
@require_auth()
def list_servers():
    # compile list of servers
    servers = []

    for s in current_app.meta.getAllServers():
        servers.append({
            'id': s.id(),
            'name': get_server_conf(current_app.meta, s, 'registerName'),
            'address': '%s:%s' % (
                get_server_conf(current_app.meta, s, 'host'),
                get_server_port(current_app.meta, s),
            ),
            'running': s.isRunning(),
            'uptime': s.getUptime() if s.isRunning() else 0,
            'fuzzy_uptime': str(
                timedelta(seconds=s.getUptime()) if s.isRunning() else ''
            ),
            'users': (s.isRunning() and len(s.getUsers())) or 0,
            'maxusers': get_server_conf(current_app.meta, s, 'users') or 0
        });

    return jsonify(servers=servers)


@mmctlui.route('/api/get-global-config/')
@require_auth()
def get_global_config():
    conf = current_app.meta.getDefaultConf()

    return jsonify(globalConf = conf)


@mmctlui.route('/api/create-server/', methods=('POST',))
@require_auth()
def create_server():
    server = current_app.meta.newServer()

    return jsonify(server_id=server.id())


@mmctlui.route('/api/delete-server/', methods=('POST',))
@require_auth()
def delete_server():
    server = current_app.meta.getServer(request.json['server_id'])

    if server.isRunning():
        server.stop()

    server.delete()

    return jsonify()


@mmctlui.route('/api/stop-server/', methods=('POST',))
@require_auth()
def stop_server():
    server = current_app.meta.getServer(request.json['server_id'])
    server.stop();

    return jsonify()


@mmctlui.route('/api/start-server/', methods=('POST',))
@require_auth()
def start_server():
    server = current_app.meta.getServer(request.json['server_id'])
    server.start();

    return jsonify()


@mmctlui.route('/api/get-server-config/<int:server_id>/')
@require_auth()
def get_server_config(server_id):
    server = current_app.meta.getServer(server_id)
    defaultConfig = current_app.meta.getDefaultConf()

    config = server.getAllConf()
    address = config.get('registerhostname', None) or\
              current_app.config['SERVER_HOSTNAME']
    server_port = get_server_port(current_app.meta, server, config['port'])
    if current_app.config['MUMBLE_DEFAULT_PORT'] != server_port:
        address += ':%d' % server_port

    return jsonify(
        serverId = server.id(),
        isRunning = server.isRunning(),
        config = config,
        defaultConfig = defaultConfig,
        uptime = server.getUptime() if server.isRunning() else 0,
        fuzzyUptime = str(
            timedelta(seconds=server.getUptime()) if server.isRunning() else ''
        ),
        connectLink = 'mumble://%s' % (address),
    )


@mmctlui.route('/api/get-server-log/<int:server_id>/')
@mmctlui.route('/api/get-server-log/<int:server_id>/<int:page>/')
@require_auth()
def get_server_log(server_id, page):
    server = current_app.meta.getServer(server_id)
    log_entries = []

    # Murmur documentation bug:
    # getLog doesn't take (first, last) arguments, but rather
    # first, amount
    per_page = current_app.config['SERVER_LOG_PAGER_PER_PAGE']
    for l in server.getLog((page-1)*per_page, per_page):
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


@mmctlui.route('/api/save-server-config/<int:server_id>/', methods=('POST',))
@require_auth()
def save_server_config(server_id):
    server = current_app.meta.getServer(server_id)

    for k,v in request.json['config'].iteritems():
        server.setConf(k, v)

    return api_get_server_config(server_id)


@mmctlui.route('/api/get-server-tree/<int:server_id>/')
@require_auth()
def get_server_tree(server_id):
    server = current_app.meta.getServer(server_id)

    tree = obj_to_dict(server.getTree())
    return jsonify(tree=tree)
