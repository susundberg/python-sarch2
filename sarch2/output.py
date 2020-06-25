
VERBOSE=False

def info(string, *pargs):

    string = string.format(*pargs)
    print(string)


def debug(string, *pargs):
    if not VERBOSE:
        return 
    string = string.format(*pargs)
    print(string)
