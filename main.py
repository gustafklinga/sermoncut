"""
Startpoint for sermoncut
"""

import faulthandler
from sermoncut.sermoncut import main

def set_up_fault_handling():
    """
    Set up the Python fault handler
    """
    # Fault handler to log to an error log file
    faulthandler.enable(file=open("crash.log", "wb"))

def start():
    """
    Instantiate and run application
    """
    set_up_fault_handling()
    main()

if __name__ == '__main__':
    start()