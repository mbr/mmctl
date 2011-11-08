#!/usr/bin/env python
# coding=utf8

from flask import Blueprint

cfgutil = Blueprint('cfgutil', __name__,
                    template_folder='templates')

@cfgutil.route('/')
def index():
    return 'HELLO'
