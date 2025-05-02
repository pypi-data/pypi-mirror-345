import threading
import itertools
import time
import sys

"""
This class provides a simple spinner that can be used to indicate that a process is running.
"""

class Spinner:
    def __init__(self, delay=0.1):
        """ Spinner constructor with delay between updates. """
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.running = False

    def spin(self):
        """ Spin the spinner by refreshing the whole line. """
        while self.running:
            sys.stdout.write('\r' + next(self.spinner) + ' Loading... ')  # Refresh the entire line
            sys.stdout.flush()
            time.sleep(self.delay)

    def start(self):
        """ Start the spinner in a separate thread. """
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        """ Stop the spinner and clean the line. """
        self.running = False
        self.thread.join()  # Wait for the spinner thread to finish
        sys.stdout.write('\r' + ' ' * 20 + '\r')  # Clear the line by overwriting with blanks
        sys.stdout.flush()
