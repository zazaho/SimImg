#!/usr/bin/python3
''' Project to display similar images from an image catalog '''
import sys
import classes.main as MAIN

if __name__ == "__main__":
    ' Main routine, shim, do all work inside simim_app '

    # interpret the commandline arguments or lack thereof
    if len(sys.argv) == 1:
        pathargs = ['./']
    else:
        pathargs = sys.argv[1:]

    app = MAIN.simim_app(arguments=pathargs)
    app.mainloop()
