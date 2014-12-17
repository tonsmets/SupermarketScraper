from colorama import Fore, Back, Style
import util.settings as settings

# Log a verbose debug message
def LogD(message):
	if settings.verbose:
		print("{0}# [DEBUG] {1}{2}".format(Fore.YELLOW, message, Fore.RESET))

# Log an error message
def LogE(info, exception):
	if settings.debugging:
		print("{0}# [ERROR] {1}{2}".format(Fore.RED, info, Fore.RESET))
		print("{0}# [TRACEBACK] {1}{2}".format(Fore.RED, exception, Fore.RESET))

# Log an info message
def LogI(message):
	print("{0}# [INFO] {1}{2}".format(Fore.WHITE, message, Fore.RESET))

# Log a help message
def LogH(message):
	print("{0}# [HELP] {1}{2}".format(Fore.MAGENTA, message, Fore.RESET))

def PrintLine():
	print("# =============================================================================== #")