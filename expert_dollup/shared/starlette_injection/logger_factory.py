from logging import Logger
from .late_binding import LateBinder


LoggerFactory = LateBinder[Logger, str]
