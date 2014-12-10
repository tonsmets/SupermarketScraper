import supermarkets.ah as ah
import supermarkets.c1000 as c1000
import supermarkets.coop as coop
import supermarkets.deka as deka
import supermarkets.dirk as dirk
import supermarkets.janlinders as janlinders
import supermarkets.jumbo as jumbo

from util.logging import *
import util.settings as settings

def test():
	print("Runner")

def run():
	#ah.fetch()
	#c1000.fetch()
	#coop.fetch()
	#deka.fetch()
	dirk.fetch() # Problematic on some urls
	#janlinders.fetch()
	#jumbo.fetch()