import sys
import traceback
import util.settings
from util.logging import *
from pymongo import *

try:
	client = MongoClient(util.settings.mongoUrl)
	db = client[util.settings.dbname]
	collection = db[util.settings.collection]
	metacollection = db[util.settings.metacollection]
except:
	e = None
	if util.settings.debugging:
		e = traceback.format_exc()
	else:
		e = sys.exc_info()[0]
	LogE("Database failure! Unable to connect to: '{0}'".format(settings.mongoUrl), "{0}".format(e))
	sys.exit()

def insert(data):
	collection.insert(data)

def insertMeta(data):
	metacollection.insert(data)