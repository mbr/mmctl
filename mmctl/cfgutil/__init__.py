#!/usr/bin/env python
# coding=utf8

from flask import Blueprint, render_template, current_app
from .. import defaults

cfgutil = Blueprint('cfgutil', __name__,
                    template_folder='templates')

@cfgutil.route('/')
def index():
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
