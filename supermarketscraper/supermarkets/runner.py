import supermarkets.ah as ah
import supermarkets.c1000 as c1000
import supermarkets.coop as coop
import supermarkets.deka as deka
import supermarkets.dirk as dirk
import supermarkets.janlinders as janlinders
import supermarkets.jumbo as jumbo
import supermarkets.aldi as aldi
import supermarkets.poiesz as poiesz

from util.logging import *
import util.settings as settings

def test():
	print("Runner")

def run():
	# ah.meta()
	# c1000.meta()
	# coop.meta()
	# deka.meta()
	# dirk.meta()

	ah.fetch()
	c1000.fetch()
	coop.fetch()
	deka.fetch()
	dirk.fetch()
	janlinders.fetch()
	jumbo.fetch()
	aldi.fetch()
	poiesz.fetch()