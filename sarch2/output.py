


def info( string, *pargs ):
    
    string = string.format( *pargs )
    print(string)


def debug( string, *pargs ):
    string = string.format( *pargs )
    print(string)
