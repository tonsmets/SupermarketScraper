import util.settings as settings
import supermarkets.runner as srunner
import time
import sys, getopt
from util.logging import *
from colorama import init

def main(argv):
	init()

	# Parsing of arguments
	try:
		#opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
		opts, args = getopt.getopt(argv,"hd",["help","debug"])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h' or opt == '--help':
			LogI("SupermarketScraper Help function")
			LogI("Permitted parameters are:")
			LogI("-h, --help (Show this info)")
			LogI("-d, --debug (Verbose logging)")
			#LogI("# -t, --tor")
			sys.exit()
		elif opt == '-d' or opt == '--debug':
			settings.debugging = True
	# End of argument parsing

	start_time = time.time() * 1000

	settings.print_info()

	if settings.debugging:
		LogD("Debugging enabled!!\n")

	srunner.run()

	seconds = (time.time() * 1000) - start_time
	PrintLine()
	LogI("Scraper finished in {0}ms.\n".format(format(seconds, '.2f')))
	

if __name__ == '__main__':
	main(sys.argv[1:])