from pathlib import Path
import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig(level=logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('bfgcp: %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

def log(frame, obj):
    """Create log message and return the object."""
    path = Path(frame[0][1])
    module = path.stem
    line = frame[0][2]
    message_text = f'{obj} <{module}> {line}'
    logger.debug(message_text)
    return obj

