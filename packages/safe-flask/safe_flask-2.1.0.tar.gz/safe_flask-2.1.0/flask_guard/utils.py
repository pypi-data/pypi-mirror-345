import re
import logging
import json
from urllib.parse import parse_qs
from flask_guard.rules import RULES, WHITELIST

logger = logging.getLogger("FlaskGuard")

def is_request_malicious(environ, body=None, post_data=None):
    """
    Analyze the request for malicious patterns based on defined rules.
    :param environ: WSGI environment dictionary.
    :param body: Optional POST request body.
    :param post_data: Parsed POST request parameters.
    :return: True if the request is malicious, False otherwise.
    """
    query_string = environ.get('QUERY_STRING', '')
    user_agent = environ.get('HTTP_USER_AGENT', 'Unknown User-Agent')

    # Check whitelist for query string and user agent independently
    if is_whitelisted(query_string, "query_string") and is_whitelisted(user_agent, "user_agent"):
        return False

    # Check each rule in the RULES dictionary
    for rule_name, rule in RULES.items():
        if rule.get("enabled", False):
            pattern = rule.get("pattern")
            targets = rule.get("target", ["query_string"])  # Ensure targets is a list
            if not isinstance(targets, list):
                targets = [targets] 

            try:
                for target in targets:
                    if target == "query_string" and re.search(pattern, query_string, re.IGNORECASE):
                        log_blocked_request(environ, rule_name, target)
                        return True
                    elif target == "user_agent" and re.search(pattern, user_agent, re.IGNORECASE):
                        log_blocked_request(environ, rule_name, target)
                        return True
                    elif target == "post_body" and post_data:
                        for key, values in post_data.items():
                            for value in values:
                                if re.search(pattern, value, re.IGNORECASE):
                                    log_blocked_request(environ, rule_name, target, key=key, value=value)
                                    return True
            except re.error as e:
                logger.error(f"Invalid regex pattern in rule '{rule_name}': {e}")

    return False

def is_response_malicious(response_body):
    """
    Analyze the response body for malicious patterns (e.g., directory listing).
    :param response_body: The response body as a string.
    :return: True if the response is malicious, False otherwise.
    """
    for rule_name, rule in RULES.items():
        if rule.get("enabled", False) and rule.get("target") == "response_body":
            pattern = rule.get("pattern")
            try:
                if pattern and re.search(pattern, response_body, re.IGNORECASE):
                    logger.warning(f"\033[91mBlocked response: Rule={rule_name}, ResponseBody={response_body[:100]}...\033[0m")
                    return True
                if rule_name == "directory_listing" and "<a href=" in response_body and "</a>" in response_body:
                    logger.warning(f"\033[91mBlocked response: Rule={rule_name}, Detected directory listing structure.\033[0m")
                    return True
            except re.error as e:
                logger.error(f"Invalid regex pattern in rule '{rule_name}': {e}")
    return False

def is_whitelisted(value, target):
    """
    Check if the value matches any whitelist pattern for the given target.
    :param value: The value to check (e.g., query string or user agent).
    :param target: The target type (e.g., "query_string" or "user_agent").
    :return: True if the value is whitelisted, False otherwise.
    """
    for pattern in WHITELIST.get(target, []):
        try:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        except re.error as e:
            logger.error(f"Invalid regex pattern in whitelist for target '{target}': {e}")
    return False

def log_blocked_request(environ, rule_name, target, key=None, value=None):
    """
    Log details of a blocked request for debugging and improvement.
    :param environ: WSGI environment dictionary.
    :param rule_name: The name of the rule that triggered the block.
    :param target: The target that triggered the block (e.g., query_string, post_body).
    :param key: Optional key for POST data (if applicable).
    :param value: Optional value for POST data (if applicable).
    """
    query_string = environ.get('QUERY_STRING', '')
    user_agent = environ.get('HTTP_USER_AGENT', 'Unknown User-Agent')

    if target == "post_body" and key and value:
        logger.warning(
            f"\033[91mBlocked request: Rule={rule_name}, Target={target}, Key={key}, Value={value}, UserAgent={user_agent}\033[0m"
        )
    else:
        logger.warning(
            f"\033[91mBlocked request: Rule={rule_name}, Target={target}, QueryString={query_string}, UserAgent={user_agent}\033[0m"
        )

def parse_post_data(body, content_type):
    """
    Parse POST request body into a dictionary of parameters.
    :param body: Raw POST request body.
    :param content_type: Content-Type header of the request.
    :return: Dictionary of parsed parameters.
    """
    try:
        if "application/json" in content_type:
            return json.loads(body)
        return parse_qs(body)
    except Exception as e:
        logger.error(f"Failed to parse POST data: {e}")
        return {}
