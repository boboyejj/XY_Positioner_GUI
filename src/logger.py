import logging

#logging.basicConfig(filename="NS Testing.log", level=logging.INFO)

logger = logging.getLogger('user')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(message)s')

file_handler = logging.FileHandler("NS Testing.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
