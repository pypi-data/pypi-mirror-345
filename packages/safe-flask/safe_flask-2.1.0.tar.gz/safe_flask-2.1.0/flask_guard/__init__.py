import logging
import os
from flask_guard.middleware import FirewallMiddleware

# Configure FlaskGuard logger
logger = logging.getLogger("FlaskGuard")
logger.setLevel(logging.INFO)

class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter to add colors to log messages.
    """
    COLORS = {
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Orange
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m",  # Reset color
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        message = super().format(record)
        return f"{color}{message}{reset}"

# Set up the logger with the color formatter
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

def FlaskGuard(app, config=None, custom_blocked_response=None):
    """
    Initialize FlaskGuard with the given Flask app.
    :param app: Flask application instance.
    :param config: Optional configuration dictionary.
    :param custom_blocked_response: Optional function to generate a custom blocked response.
    """
    if config:
        app.config.update(config)
    app.wsgi_app = FirewallMiddleware(app.wsgi_app, custom_blocked_response=custom_blocked_response)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.info("Thank you for using FlaskGuard! Your application is now secured and protected.")
