#!/usr/bin/env python
# coding=utf8

from mmctl import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
