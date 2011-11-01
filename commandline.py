#!/usr/bin/env python
# coding=utf8

import argparse

parser = argparse.ArgumentParser(description='Manage a murmur server')
parser.add_argument('--slice-file',
                    help='Path to the mumble servers slice file.',
                    default='Murmur.ice')
parser.add_argument('--server-url',
                    help='Server url (mumble://host:port) to connect to '\
                    'using ice.',
                    default='mumble://localhost:6502')
