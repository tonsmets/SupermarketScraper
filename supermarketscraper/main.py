import util.settings as settings
import supermarkets.runner as srunner
import time

if __name__ == '__main__':
	start_time = time.time() * 1000

	settings.print_info()
	srunner.run()

	seconds = (time.time() * 1000) - start_time
	print("#===============================================================================#")
	print("# SCRAPER FINISHED IN {0}ms.\n".format(format(seconds, '.2f')))
	