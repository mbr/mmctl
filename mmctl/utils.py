#!/usr/bin/env python
# coding=utf8

from math import ceil
import os

from flask import current_app

import Ice

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


# does not handle recursion well at all!
def obj_to_dict(obj):
    rv = {'_type': str(type(obj))}

    if type(obj) in (bool, int, float, str, unicode):
        return obj

    if type(obj) in (list, tuple):
        return [obj_to_dict(item) for item in obj]

    if type(obj) == dict:
        return dict((k, obj_to_dict(v)) for k, v in obj.iteritems())

    return obj_to_dict(obj.__dict__)


def get_server_conf(meta, server, key):
    val = server.getConf(key)
    if '' == val:
        val = meta.getDefaultConf().get(key, '')
    return val


def get_server_port(meta, server, val=None):
    val = server.getConf('port') if val == None else val

    if '' == val:
        val = meta.getDefaultConf().get('port', 0)
        val = int(val) + server.id() - 1

    return int(val)


def load_meta(ice_string):
    Ice.loadSlice(os.path.join(current_app.root_path, 'Murmur.ice'))
    import Murmur

    ic = Ice.initialize()

    metaproxy = ic.stringToProxy(ice_string)
    return Murmur.MetaPrx.checkedCast(metaproxy)
