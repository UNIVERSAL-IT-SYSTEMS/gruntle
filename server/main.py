# coding=UTF-8
#
# thickishstring server
# Copyright © 2013 David Given
#
# This software is redistributable under the terms of the Simplified BSD
# open source license. Please see the COPYING file in the distribution for
# the full text.

from gevent import monkey; monkey.patch_all()
import gevent

from ws4py.server.geventserver import WebSocketServer
from ws4py.websocket import EchoWebSocket

import sys
import argparse
import logging
import cPickle as pickle

# Internal modules

import ts.db as db
from ts.connection import Connection
from ts.DBRealm import DBRealm
from ts.DBPlayer import DBPlayer

# Basic setup

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.info("fnord")

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

db.open(args.filename)
if not db.isset("root"):
	logging.info("initialising new database")
	db.set("root", True)
	db.set(("root", "nextobj"), 1)
	
	thoth = DBPlayer()
	thoth.create("Thoth", "<no email address>", "testpassword")
	
	defaultrealm = thoth.addRealm("The Hub")
	defaultinstance = defaultrealm.addInstance()
	
	e = defaultrealm.findRoom("entrypoint")
	r = defaultrealm.addRoom("closet", "Broom Closet", "It's full of junk.")
	
	e.actions = {
		0:
		{
			"description": "Head downstairs to the broom closet?",
			"type": "room",
			"target": "closet"
		}
	}
	
	r.actions = {
		0:
		{
			"description": "It's boring here; head back upstairs.",
			"type": "room",
			"target": "entrypoint"
		}
	}
	
	defaultinstance.players = frozenset({thoth})
	thoth.instance = defaultinstance
	thoth.room = e
	db.set(("root", "defaultinstance"), defaultinstance)

# Create and start the server.

logging.info("opening socket")
server = WebSocketServer(
	('0.0.0.0', args.port),
	websocket_class=Connection
)

logging.info("listening...")
server.serve_forever()

