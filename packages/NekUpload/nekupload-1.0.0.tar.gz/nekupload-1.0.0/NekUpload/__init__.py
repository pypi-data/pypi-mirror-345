__version__="0.1.0"

import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#also read logs to a file
#file_handler = logging.FileHandler("info.log", mode='w')
#file_handler.setLevel(logging.INFO)
#file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

#logging.getLogger().addHandler(file_handler)

#LOG_FILE_PATH = os.path.abspath("info.log")
#MODULE_ABS_PATH = os.path.dirname(os.path.abspath(__file__))