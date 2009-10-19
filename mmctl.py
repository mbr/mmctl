#!/usr/bin/env python

import socket
import urllib
from email.mime.text import MIMEText
import smtplib
import dbus
import sys
from getpass import getpass
from optparse import OptionParser

murmur_bus_name = 'net.sourceforge.mumble.murmur'
meta_interface = 'net.sourceforge.mumble.Meta'
server_interface = 'net.sourceforge.mumble.Murmur'

default_mailserver = 'localhost'
default_mailport = 25

class MurmurMeta(object):
	def __init__(self, bus):
		self.obj = bus.get_object(murmur_bus_name, '/')
		self.bus = bus

	def getAllServers(self):
		return map(lambda i: MurmurServer(self, i), list(self.obj.getAllServers(dbus_interface = meta_interface)))

	def getDefaultConf(self):
		return dict(self.obj.getDefaultConf(dbus_interface = meta_interface))

	def getServer(self, id):
		return MurmurServer(self, id)

	def newServer(self):
		return MurmurServer(self, self.obj.newServer(dbus_interface = meta_interface))

class MurmurServer(object):
	def __init__(self, meta, id):
		self.meta = meta
		self.id = id
		self.obj = self.meta.bus.get_object(murmur_bus_name, '/%d' % id)

	def getConfig(self):
		conf = self.meta.getDefaultConf()
		conf.update(dict(self.meta.obj.getAllConf(self.id, dbus_interface = meta_interface)))
		return conf

	def setConfig(self, key, value):
		conf = self.meta.obj.setConf(self.id, key, value, dbus_interface = meta_interface)

	def getUserById(self, id):
		u = MurmurUser(self)
		u._load(id)
		return u

	def getAllUsers(self):
		return map(lambda data: self.getUserById(data[0]), self.obj.getRegisteredPlayers("", dbus_interface = server_interface))

	def deleteUser(self, id):
		self.obj.unregisterPlayer(id, dbus_interface = server_interface)

	def start(self):
		self.meta.obj.start(self.id, dbus_interface = meta_interface)

	def stop(self):
		self.meta.obj.stop(self.id, dbus_interface = meta_interface)

	def destroy(self):
		self.meta.obj.deleteServer(self.id, dbus_interface = meta_interface)

	def __unicode__(self):
		return u"<Server:%d>" % self.id

	def __repr__(self):
		return self.__unicode__()

class MurmurUser(object):
	id = None
	name = "unnamed"

	def __init__(self, server):
		self.server = server

	def _load(self, id):
		data = self.server.obj.getRegistration(id, dbus_interface = server_interface)
		self.id = id
		self.name = data[1]
		self.email = data[2]
	
	def save(self):
		if None == self.id:
			self.id = self.server.obj.registerPlayer(self.name, dbus_interface = server_interface)

		if hasattr(self,'password'): self.server.obj.setRegistration(self.id, self.name, self.email, self.password, dbus_interface = server_interface)
		else:
			self.server.obj.updateRegistration( (self.id, self.name, self.email, ''), dbus_interface = server_interface )
		return self.id

	def __unicode__(self):
		return u"<User:Id %d/Server %d/Name %s>" % (self.id, self.server.id, self.name)

	def __repr__(self):
		return self.__unicode__()

# a fatal error occured, output msg and exit
def fatal(msg):
	sys.stderr.write(msg + "\n")
	sys.exit(1)

def nargs(action, args, arg_names):
	if len(args) != len(arg_names):
		fatal("%s requires the following arguments: %s" % (action, ", ".join(arg_names)))

def reqopt(opts, opt_reqs):
	for opt in opt_reqs:
		if not hasattr(opts, opt) or None == getattr(opts,opt): fatal("%s requires the following options: %s. See --help for details." % (opts.action, " ".join(opt_reqs)))

def formatconfig(k, v):
	return "** %s **\n%s\n" % (k,v)

def sendmail(to_address, subject, body):
	(host, port) = urllib.splitnport(opts.mailserver, default_mailport)

	m = MIMEText(body)
	m['Subject'] = subject
	m['To'] = to_address

	from_address = None
	if not opts.from_address:
		server = meta.getServer(opts.server)
		u = server.getUserById(1)
		if not u.email:
			print u"cannot send email - no email set for %s" % u
			return
		from_address = '%s <%s>' % (u.name, u.email)
	else:
		from_address = opts.from_address

	m['From'] = from_address

	s = smtplib.SMTP(host, port)
	s.sendmail(m['From'], m['To'], m.as_string())
	print u"sent email from %s to %s: %s" % (m['From'], m['To'], m['Subject'])

# parse options
parser = OptionParser(version="%prog 0.1",
                      description="A command-line interface for murmur, the mumble server.")
parser.add_option("-S","--session", dest="session", help="use session instead of system DBUS", action="store_true", default=False)
parser.add_option("-s","--server", dest="server", help="server id (only used with some commands)", type="int", action="store")
parser.add_option("-u","--user", dest="user", help="user id to be modified (only used with some commands)", type="int", action="store")
parser.add_option("-L","--list-servers", dest="action", help="list servers", action="store_const", const="list-servers")
parser.add_option("-n","--new-server", dest="action", help="create a new server", action="store_const", const="new-server")
parser.add_option("-D","--delete-server", dest="action", help="delete a server", action="store_const", const="delete-server")
parser.add_option("-c","--create-user", dest="action", help="create a new user (name, email)", action="store_const", const="create-user")
parser.add_option("-d","--delete-user", dest="action", help="delete a user", action="store_const", const="delete-user")
parser.add_option("-l","--list-users", dest="action", help="list users", action="store_const", const="list-users")
parser.add_option("-e","--change-email", dest="action", help="change a user's email", action="store_const", const="change-email")
parser.add_option("-p","--change-password", dest="action", help="change a user's password", action="store_const", const="change-password")
parser.add_option("-g","--print-config", dest="action", help="print configuration values (optional: value)", action="store_const", const="print-config")
parser.add_option("-G","--set-config", dest="action", help="set configuration value (key, value)", action="store_const", const="set-config")
parser.add_option("-r","--start", dest="action", help="start server", action="store_const", const="start")
parser.add_option("-R","--restart", dest="action", help="restart server", action="store_const", const="restart")
parser.add_option("-t","--stop", dest="action", help="stop server", action="store_const", const="stop")
parser.add_option("","--testmail", dest="action", help="test email sending capabilities (will send an email to specified user)", action="store_const", const="testmail")
parser.add_option("-M","--mailserver", dest="mailserver", help="The mailserver address to use. Defaults to 'localhost:25'.", action="store", default=default_mailserver)
parser.add_option("-F","--from-address", dest="from_address", help="The From: address used when sending an email. Defaults to the email address of the user with uid 1.")
parser.add_option("-E","--send-mail", action="store_true", dest="send_mail", default=False, help="send an email to a user when his password changed or his account got created")

(opts, args) = parser.parse_args()

# use session or system dbus
meta = MurmurMeta(dbus.SessionBus() if opts.session else dbus.SystemBus())

if not opts.action: fatal("No action specified. See --help for a list of actions")

if "list-servers" == opts.action:
	tpl =    "%3d  %15s  %5d  %s" 
	header = "%3s  %15s  %-5s  %s" % ("id","host","port","name")
	print header
	for server in meta.getAllServers():
		conf = server.getConfig()
		print tpl % (server.id, conf['host'], int(conf['port']), conf['registername'])
elif "start" == opts.action:
	reqopt(opts, ['server'])
	server = meta.getServer(opts.server)
	print "stopping server %d..." % server.id
	server.start()
elif "stop" == opts.action:
	reqopt(opts, ['server'])
	server = meta.getServer(opts.server)
	print "stopping server %d..." % server.id
	server.stop()
elif "restart" == opts.action:
	reqopt(opts, ['server'])
	server = meta.getServer(opts.server)
	print "restarting server %d..." % server.id
	server.stop()
	server.start()
elif "new-server" == opts.action:
	server = meta.newServer()
	print server
elif "delete-server" == opts.action:
	reqopt(opts, ['server'])
	server = meta.getServer(opts.server)
	sid = server.id
	server.destroy()
	print "deleted server %d" % sid
elif "print-config" == opts.action:
	reqopt(opts, ['server'])
	server = meta.getServer(opts.server)
	if 0 == len(args):
		for (k,v) in server.getConfig().items():
			print formatconfig(k,v)
	elif 1 == len(args):
		try:
			print formatconfig(args[0], server.getConfig()[args[0]])
		except KeyError:
			fatal("No configuration options \"%s\"" % args[0])
	else:
		fatal("Too many arguments for print-config")
elif "set-config" == opts.action:
	reqopt(opts, ['server'])
	nargs(opts.action, args, ['key','value'])
	server = meta.getServer(opts.server)
	server.setConfig(args[0],args[1])
	print formatconfig(args[0], server.getConfig()[args[0]])
elif "list-users" == opts.action:
	reqopt(opts, ['server'])
	tpl =    "%4d  %20s  %20s"
	header = "%4s  %20s  %20s" % ("id", "user", "email")
	print header
	for user in meta.getServer(opts.server).getAllUsers():
		print tpl % (user.id, user.name, user.email)
elif "create-user" == opts.action:
	nargs(opts.action, args, ['name','email'])
	server = meta.getServer(opts.server)
	user = MurmurUser(server)
	user.password = 'foo'
	user.name = args[0]
	user.email = args[1]
	user.save()
	print "new user: %s" % user
	if opts.send_mail:
		if user.email:
			sendmail(user.email, "Mumble account created.", "Hello %s,\r\n\r\nyour new mumble account is ready.\r\n\r\nYour username: %s\r\n\r\nBest regards,\r\n\r\n%s (admin)" % (user.name, user.name, server.getUserById(1).name))
		else:
			print "not sending email, because user does not have an email address registered"
elif "delete-user" == opts.action:
	reqopt(opts, ['server','user'])
	server = meta.getServer(opts.server)
	server.deleteUser(opts.user)
	print "removed user id: %d" % opts.user
elif "change-password" == opts.action:
	reqopt(opts, ['server','user'])
	server = meta.getServer(opts.server)
	user = server.getUserById(opts.user)
	pw = getpass("new password for %s: " % user.name)
	user.password = pw
	user.save()
	print "password changed"
	if opts.send_mail:
		if user.email:
			sendmail(user.email, "Your mumble password has been changed.", "Hello %s,\r\n\r\nyour password on has been changed to \r\n\r\n%s\r\n\r\nby the administrator. You may keep a copy of this email for future reference.\r\n\r\nBest regards,\r\n\r\n%s (admin)" % (user.name, pw, server.getUserById(1).name))
		else:
			print "not sending email, because user does not have an email address registered"
elif "change-email" == opts.action:
	reqopt(opts, ['server','user'])
	server = meta.getServer(opts.server)
	nargs(opts.action, args, ['email'])
	user = server.getUserById(opts.user)
	user.email = args[0]
	user.save()
	print "email changed"
elif "testmail" == opts.action:
	reqopt(opts, ['server'])
	nargs(opts.action, args, ['email'])
	sendmail(args[0], 'Mumble server test message', 'If you can read this message, your mumble server can send email. It will use the user with uid 1 as the sender.')
else:
	fatal("Unknown action \"%s\" - this should not happen" % action)
