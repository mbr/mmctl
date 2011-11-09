#!/usr/bin/env python
# coding=utf8

from flask import Blueprint, render_template, current_app, jsonify, request
from ..utils import load_meta
from .. import defaults

import datetime
import os

import Ice

cfgutil = Blueprint('cfgutil', __name__,
                    template_folder='templates')

@cfgutil.route('/', methods=('GET', 'POST',))
def index():
    if 'POST' == request.method:
        form = request.form

        current_app.jinja_env.filters['repr'] = lambda v: repr(v)

        # save configuration file
        conffile = os.path.join(current_app.instance_path, 'mmctl.conf')
        try:
            with open(conffile, 'w') as c:
                c.write(render_template('mmctl.conf',
                    dt=datetime.datetime.now(),
                    ice_string=form['icestring'],
                    server_hostname=form['hostname'],
                    mmctl_password_key=form['pbdk'],
                    pbkdf2_salt=current_app.initial_salt,
                    pbkdf2_iterations=current_app.initial_iterations,
                    pbkdf2_keylength=current_app.initial_keylength
                ))
        except IOError:
            return render_template('error.html',
                                   conffile=conffile)

        # display success message
        return render_template('success.html')
    else:
        form = {
            'icestring': defaults.ICE_STRING,
            'hostname': defaults.SERVER_HOSTNAME,
        }
    return render_template('index.html',
                           version=current_app.version,
                           form=form,
                           initial_salt=current_app.initial_salt,
                           initial_iterations=current_app.initial_iterations,
                           initial_keylength=current_app.initial_keylength)


@cfgutil.route('/check-proxy/', methods=('POST',))
def check_proxy():
    error = False
    try:
        meta = load_meta(request.json['proxy'])
    except Ice.DNSException, e:
        error = 'Could not resolve host "%s"' % e.host
    except Ice.ConnectionRefusedException, e:
        error = 'Connection refused'
    except Ice.NoEndpointException, e:
        error = 'No endpoint at "%s"' % e.proxy
    except Ice.ObjectNotExistException, e:
        error = 'Object "%s" does not exist' % e.id.name
    except Exception, e:
        error = str(e)
    finally:
        return jsonify(error=error)
