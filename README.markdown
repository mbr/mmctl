mmctl
=====
mmctl let's you administrate Murmur, the [Mumble][1] server that currently comes without a default administration interface.

Features
--------
* Webbased UI supporting many servers
* Connect through any accessible [Ice][2] interface
* Pure AJAX-interface that feels like a Desktop application
* Looks great thanks to [Bootstrap][3]

Installing
----------
mmctl is currently under development. It's fully functional and working, but there aren't detailed instructions for installing it yet. Here's what you need:

* It's a [Flask][4]-based WSGI app, so you need Python.
* Required python packages (from PyPI) are: Flask, Flask-Assets, cssmin.
* You will also need python support for ZeroC's Ice. Look for a package named "python-zeroc-ice" (Ubuntu) or "ice-python" (Fedora).
* [VirtualEnv][5] highly recommend

The steps:

* (install Ice Python support through apt-get or yum or whatever your distro of choice uses)
* virtualenv mmctl
* . mmctl/bin/activate
* pip install Flask Flask-Assets cssmin
* git clone git://github.com/mbr/mmctl.git
* python mmctl/runserver.py

This will run a server listening on port 5000. Open up http://localhost:5000 (replace localhost with your server IP if it's remote) and set up the initial configuration.

Afterwards, kill the server with C-c and restart it to load the generated configuration.

[1]: http://mumble.sourceforge.net "Mumble homepage"
[2]: http://zeroc "ZeroC homepage"
[3]: http://twitter.github.com/bootstrap/ "Bootstrap, from Twitter"
[4]: http://flask.pocoo.org "Flask"
[5]: http://flask.pocoo.org/docs/installation/#virtualenv "virtualenv installation instructions from the Flask manual."
