import util.settings as settings
from pymongo import *

client = MongoClient(settings.mongoUrl)
db = client[settings.dbname]
collection = db.data