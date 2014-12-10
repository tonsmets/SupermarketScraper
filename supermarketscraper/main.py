import util.settings as settings
import supermarkets.runner as srunner
import time
from util.logging import *
from colorama import init

if __name__ == '__main__':
	init()
	start_time = time.time() * 1000

	settings.print_info()

	if settings.debugging:
		LogD("Debugging enabled!!\n")

	srunner.run()

	seconds = (time.time() * 1000) - start_time
	PrintLine()
	LogI("Scraper finished in {0}ms.\n".format(format(seconds, '.2f')))
	