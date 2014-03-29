# coding=UTF-8
#
# thickishstring server
# Copyright © 2013 David Given
#
# This software is redistributable under the terms of the Simplified BSD
# open source license. Please see the COPYING file in the distribution for
# the full text.

import gevent

from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

import sys
import argparse
import logging
import apsw
import hashlib

# Internal modules

import ts.db as db
from ts.connection import Connection
from ts.DBRealm import DBRealm
from ts.DBPlayer import DBPlayer
from ts.DBInstance import *

# Basic setup

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

parser = argparse.ArgumentParser(
	description = "thickishstring prototype Python server"
)

parser.add_argument(
	'--db', '-d',
	default = 'test.db',
	dest = 'filename',
	help = 'specifies the database file to use'
)
parser.add_argument(
	'--port', '-p',
	default = 8086,
	dest = 'port',
	help = 'which port to listen on'
)

args = parser.parse_args()

# Open and initialise the database.

if not db.connect(args.filename, "server/dbinit.sql"):
	s = open("server/dbinit.sql").read().decode("UTF-8")
	logging.info("initialising new database")
	c = db.sql.cursor()
	c.execute(s)

	with db.sql:		
		thoth = DBPlayer()
		thoth.create("Thoth", "<no email address>",
			hashlib.sha256("testpassword").hexdigest())
		
		defaultrealm = thoth.addRealm("The Hub")
		defaultinstance = defaultrealm.addInstance()
		setDefaultInstance(defaultinstance)
		
		e = defaultrealm.findRoom("entrypoint")
		e.script = open("server/hub/entrypoint.tb").read().decode("UTF-8")

		r = defaultrealm.addRoom("closet", "Broom Closet",
			open("server/hub/closet.tb").read().decode("UTF-8"))

		thoth.instance = defaultinstance
		thoth.room = e

logging.info("logging out all players")
db.sql.cursor().execute("UPDATE players SET connected = 0")

# Create and start the server.

logging.info("opening socket")
server = WSGIServer(
	('0.0.0.0', args.port),
	WebSocketWSGIApplication(handler_cls=Connection)
)

logging.info("listening...")
server.serve_forever()

