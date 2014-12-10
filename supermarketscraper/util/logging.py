from colorama import Fore, Back, Style

# Log a verbose debug message
def LogD(message):
	print("{0}# [DEBUG] {1}{2}".format(Fore.YELLOW, message, Fore.RESET))

# Log an error message
def LogE(message):
	print("{0}# [ERROR] {1}{2}".format(Fore.RED, message, Fore.RESET))

# Log an info message
def LogI(message):
	print("{0}# [INFO] {1}{2}".format(Fore.WHITE, message, Fore.RESET))

def PrintLine():
	print("# =============================================================================== #")