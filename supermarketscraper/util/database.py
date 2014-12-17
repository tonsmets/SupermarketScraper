import sys
import traceback
import util.settings as settings
from util.logging import *
from pymongo import *

try:
	client = MongoClient(settings.mongoUrl)
	db = client[settings.dbname]
	collection = db[settings.collection]
except:
	e = None
	if settings.debugging:
		e = traceback.format_exc()
	else:
		e = sys.exc_info()[0]
	LogE("Database failure! Unable to connect to: '{0}'".format(settings.mongoUrl), "{0}".format(e))
	sys.exit()

def insert(data):
	collection.insert(data)