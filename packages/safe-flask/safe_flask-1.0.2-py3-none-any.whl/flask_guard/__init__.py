import logging
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

def init_app(app, config=None):
    """
    Initialize FlaskGuard with the given Flask app.
    :param app: Flask application instance.
    :param config: Optional configuration dictionary.
    """
    if config:
        app.config.update(config)
    app.wsgi_app = FirewallMiddleware(app.wsgi_app)

    # Print startup message
    logger.info("FlaskGuard initialized. Your application is now protected.")
