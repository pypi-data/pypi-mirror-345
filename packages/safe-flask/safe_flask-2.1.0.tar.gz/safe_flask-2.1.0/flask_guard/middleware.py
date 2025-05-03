from flask_guard.utils import is_request_malicious, parse_post_data, is_response_malicious
from io import BytesIO

class FirewallMiddleware:
    def __init__(self, app, custom_blocked_response=None):
        """
        Initialize the FirewallMiddleware.
        :param app: Flask application instance.
        :param custom_blocked_response: Optional function to generate a custom blocked response.
        """
        self.app = app
        self.custom_blocked_response = custom_blocked_response or self.default_blocked_response

    def default_blocked_response(self):
        """
        Default response for blocked requests or responses.
        :return: Tuple containing status code and response body.
        """
        return '403 Forbidden', [b"Request blocked by FlaskGuard firewall."]

    def __call__(self, environ, start_response):
        # Analyze the incoming request
        if is_request_malicious(environ):
            status, response_body = self.custom_blocked_response()
            start_response(status, [('Content-Type', 'text/plain')])
            return response_body
        
        # Analyze POST body if applicable
        if environ.get('REQUEST_METHOD') == 'POST':
            content_length = int(environ.get('CONTENT_LENGTH', 0) or 0)
            if content_length > 0:
                body = environ['wsgi.input'].read(content_length).decode('utf-8', errors='ignore')
                environ['wsgi.input'] = BytesIO(body.encode('utf-8'))  # Restore input stream
                post_data = parse_post_data(body, content_type=environ.get('CONTENT_TYPE', ''))
                if is_request_malicious(environ, body=body, post_data=post_data):
                    status, response_body = self.custom_blocked_response()
                    start_response(status, [('Content-Type', 'text/plain')])
                    return response_body

        # Buffer the response to analyze it before sending headers
        response_body = []

        def custom_start_response(status, headers, exc_info=None):
            self.status = status
            self.headers = headers
            self.exc_info = exc_info
            return lambda data: response_body.append(data)

        response = self.app(environ, custom_start_response)
        response_body = b"".join(response).decode('utf-8', errors='ignore')

        # Analyze the response for directory listing
        if is_response_malicious(response_body):
            status, response_body = self.custom_blocked_response()
            start_response(status, [('Content-Type', 'text/plain')])
            return response_body

        # Send the original response if it's safe
        start_response(self.status, self.headers, self.exc_info)
        return [response_body.encode('utf-8')]
