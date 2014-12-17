import util.settings as settings
import time
import sys, getopt
from util.logging import *
from colorama import init
import supermarkets.runner as srunner

def main(argv):
	init()

	# Parsing of arguments
	try:
		#opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
		opts, args = getopt.getopt(argv,"hve",["help","verbose","error"])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h' or opt == '--help':
			LogH("SupermarketScraper Help function")
			LogH("Permitted parameters are:")
			LogH("-h, --help (Show this info)")
			LogH("-v, --verbose (Verbose logging)")
			LogH("-e, --error (Error logging)")
			#LogI("# -t, --tor")
			sys.exit()
		elif opt == '-e' or opt == '--error':
			settings.debugging = True
		elif opt == '-v' or opt == '--verbose':
			settings.verbose = True
	# End of argument parsing

	start_time = time.time() * 1000

	settings.print_info()

	LogD("Debugging enabled!!\n")

	srunner.run()

	seconds = (time.time() * 1000) - start_time
	PrintLine()
	LogI("Scraper finished in {0}ms.\n".format(format(seconds, '.2f')))
	

if __name__ == '__main__':
	main(sys.argv[1:])