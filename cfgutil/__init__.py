#!/usr/bin/env python
# coding=utf8

from flask import Blueprint

cfgutil = Blueprint('cfgutil', __name__)

@cfgutil.route('/')
def index():
    return 'HELLO'
