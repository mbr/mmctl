#!/usr/bin/env python
# coding=utf8

ICE_STRING = 'Meta:tcp -h localhost -p 6502'
SLICE_FILE = 'Murmur.ice'
SERVER_HOSTNAME = 'localhost'
SERVER_LOG_PAGER_PER_PAGE = 10
MUMBLE_DEFAULT_PORT = 64738
AUTH_COOKIE_NAME = 'mmctl_auth_cookie'
AUTH_COOKIE_EXPIRY = 365  # days

# a value of None will cause a new one to be generated on app start
PBKDF2_SALT=None

# the high number of iterations prevents an attacker from trying too
# many dictionary attacks once he has the hash.
# unfortunately, this has a bit of an impact on the user experience
# for now, security trumps convenience
PBKDF2_ITERATIONS=2000
PBKDF2_KEYLENGTH=64
