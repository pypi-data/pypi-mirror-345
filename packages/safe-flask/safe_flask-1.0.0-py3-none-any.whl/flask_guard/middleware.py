from flask_guard.utils import is_request_malicious

class FirewallMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Analyze the incoming request
        if is_request_malicious(environ):
            # Block the request if malicious
            start_response('403 Forbidden', [('Content-Type', 'text/plain')])
            return [b"Request blocked by FlaskGuard firewall."]
        # Pass the request to the Flask app if safe
        return self.app(environ, start_response)
