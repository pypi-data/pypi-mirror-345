import os
import subprocess
import logging
import coloredlogs
from colorama import Fore

# Set up logging
logger = logging.getLogger(Fore.RED + " + STREAMLINK + ")
coloredlogs.install(level='DEBUG', logger=logger)

class STREAMLINK:
    def __init__(self):
        self.url = None
        self.output_name = None
        self.live_url = None
        self.binary_path = os.path.join(os.path.dirname(__file__), 'bin', 'streamlink')
        
    def streamlink_restream(self):
        pass