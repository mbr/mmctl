import pdb
#!/usr/bin/env python
# coding=utf8

from flask import current_app, request
import json


class ICEJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'ice_toString'):
            return {'$ICEREF': o.ice_toString()}

        return o.__dict__


def jsonify(*args, **kwargs):
    return current_app.response_class(
        json.dumps(dict(*args, **kwargs),
                   indent=None if request.is_xhr else 2,
                   cls=ICEJSONEncoder),
        mimetype='application/json',
    )
