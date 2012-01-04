#!/usr/bin/env python
# coding=utf8

from mmctl import create_app

if __name__ == '__main__':
    app = create_app()

    app.run(debug=True)

    # uncomment this line (and comment the one above)
    # to run non-debug on a global interface
    #app.run(debug=False, host='0.0.0.0')
