import logging
import os

log_level = logging.DEBUG

logging.basicConfig(
    level=logging.DEBUG,  # Set the global log level for all loggers
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Default formatter
    handlers=[
        logging.StreamHandler(),  # Console handler
    ],
)

# Get the logger instance (optional: usually the root logger is configured, so __name__ is not needed)
logger = logging.getLogger(__name__)

# Example: Adjust console handler level separately if needed
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setLevel(log_level)  # Set the level based on the environment
