import re
import logging
from flask_guard.rules import RULES, WHITELIST

logger = logging.getLogger("FlaskGuard")

def is_request_malicious(environ):
    """
    Analyze the request for malicious patterns based on defined rules.
    :param environ: WSGI environment dictionary.
    :return: True if the request is malicious, False otherwise.
    """
    query_string = environ.get('QUERY_STRING', '')
    user_agent = environ.get('HTTP_USER_AGENT', 'Unknown User-Agent')

    #logger.info(f"Analyzing query string: {query_string}")
    #logger.info(f"Analyzing user agent: {user_agent}")

    # Check whitelist for query string and user agent independently
    if is_whitelisted(query_string, "query_string") and is_whitelisted(user_agent, "user_agent"):
        #logger.info("Request passed whitelist check.")
        return False

    # Check each rule in the RULES dictionary
    for rule_name, rule in RULES.items():
        if rule.get("enabled", False):
            pattern = rule.get("pattern")
            target = rule.get("target", "query_string")
            try:
                if target == "query_string" and re.search(pattern, query_string, re.IGNORECASE):
                    log_blocked_request(environ, rule_name)
                    return True
                elif target == "user_agent" and re.search(pattern, user_agent, re.IGNORECASE):
                    log_blocked_request(environ, rule_name)
                    return True
            except re.error as e:
                logger.error(f"Invalid regex pattern in rule '{rule_name}': {e}")

    #logger.info("Request passed all checks.")
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
                #logger.info(f"Value '{value}' matched whitelist pattern '{pattern}' for target '{target}'")
                return True
        except re.error as e:
            logger.error(f"Invalid regex pattern in whitelist for target '{target}': {e}")
    return False

def log_blocked_request(environ, rule_name):
    """
    Log details of a blocked request for debugging and improvement.
    :param environ: WSGI environment dictionary.
    :param rule_name: The name of the rule that triggered the block.
    """
    query_string = environ.get('QUERY_STRING', '')
    user_agent = environ.get('HTTP_USER_AGENT', 'Unknown User-Agent')
    logger.warning(f"\033[91mBlocked request: Rule={rule_name}, QueryString={query_string}, UserAgent={user_agent}\033[0m")
