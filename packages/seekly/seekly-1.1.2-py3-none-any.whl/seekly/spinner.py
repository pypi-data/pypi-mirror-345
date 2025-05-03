"""
Spinner animation for command-line interfaces.
Provides visual feedback during long-running operations.
"""

import sys
import time
import threading
import itertools


class Spinner:
    """
    Displays an animated spinner in the terminal to indicate progress.
    
    This class creates a threaded spinner animation that can be started
    and stopped to provide visual feedback during long-running operations.
    The spinner is customizable with different characters and messages.
    
    Example usage:
        spinner = Spinner("Processing")
        spinner.start()
        # ... do some work ...
        spinner.stop("Completed!")
    """
    def __init__(self, message="Working", delay=0.1, chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        """
        Initialize the spinner with customizable parameters.
        
        Args:
            message (str): Message to display next to the spinner
            delay (float): Time between spinner character changes in seconds
            chars (str): String containing characters to use for the spinner animation
        """
        self.message = message
        self.delay = delay
        self.chars = chars
        self.busy = False
        self.spinner_thread = None
        self.spinner_visible = False

    def write_next(self):
        """Write the next character in the spinner animation."""
        sys.stdout.write("\r")
        for _ in range(self.spinner_visible):
            sys.stdout.write("\b \b")  # Erase previous spinner
        
        if self.busy:
            char = next(self.spinner_char)
            sys.stdout.write(f"{char} {self.message}...")
            self.spinner_visible = len(self.message) + 5  # Account for spinner, spaces, and ellipsis
            sys.stdout.flush()

    def spin(self):
        """Main loop for the spinner animation."""
        while self.busy:
            self.write_next()
            time.sleep(self.delay)

    def start(self, message=None):
        """
        Start the spinner animation in a separate thread.
        
        Args:
            message (str, optional): Override the spinner message
        """
        if message is not None:
            self.message = message
        self.busy = True
        self.spinner_char = itertools.cycle(self.chars)
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()

    def stop(self, message=None):
        """
        Stop the spinner animation.
        
        Args:
            message (str, optional): Message to display after stopping
        """
        self.busy = False
        
        # Clear spinner line
        sys.stdout.write("\r")
        for _ in range(self.spinner_visible):
            sys.stdout.write(" ")
        sys.stdout.write("\r")
        
        # Show completion message if provided
        if message:
            sys.stdout.write(f"{message}\n")
        
        sys.stdout.flush()
        
        # Wait for thread to terminate
        if self.spinner_thread and self.spinner_thread.is_alive():
            self.spinner_thread.join()
        
        self.spinner_visible = 0