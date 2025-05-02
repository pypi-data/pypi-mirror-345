import logging
from pprint import pprint as pp

from mhanndalorian_bot import API, Registry, EndPoint


class LoggingFormatter(logging.Formatter):
    """Custom logging formatter class"""

    def format(self, record):
        log_message_format = \
            '{asctime} | {levelname} | {name} | {module} : {funcName}() [{lineno:}] | {message}'
        formatter = logging.Formatter(log_message_format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

allycode = '314927874'
allycode2 = '245866537'
api_key = 'usergeneratedoNtGtKG0YW6sLSj1Q12Q7hOCVhTAgvd0xMexdLK4qZZhnQbSO1'
discord_id = '344006512546545667'
discord_id2 = '730760587864178710'

api = API(api_key, allycode)

