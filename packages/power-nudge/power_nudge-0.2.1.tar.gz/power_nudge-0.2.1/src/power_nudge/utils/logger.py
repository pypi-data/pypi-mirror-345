# logger_config.py
import sys

from loguru import logger

# Remove default handler (stdout)
logger.remove()

# Add custom handler
logger.add(sys.stdout, level="DEBUG", format="{time} | {level} | {message}")
logger.add("logs/app.log", rotation="1 MB", retention="7 days", level="INFO")

# Optional: You can export the logger explicitly
log = logger
