import copy

# Default rules
DEFAULT_RULES = {
    "sql_injection": {
        "enabled": True,
        "pattern": r"(?:')|(?:--)|(/\*(?:.|[\n\r])*?\*/)|(?:\b(select|update|delete|insert|drop|alter|create|exec|union|where|or|and)\b)|(?:\b\d+=\d+\b)|(?:\b(UNION\s+ALL\s+SELECT|INTO\s+OUTFILE|LOAD_FILE)\b)|(?:\bOR\s+1=1\b)|(?:' OR 1=1)|(?:\b' AND 1=1\b)|(?:\b' OR 'a'='a\b)|(?:\bSLEEP\(\d+\)\b)|(?:\bBENCHMARK\(\d+,.+\)\b)",
        "target": "query_string",
    },
    "xss_attack": {
        "enabled": True,
        "pattern": r"(<script.*?>.*?</script.*?>)|(<.*?javascript:.*?>)|((onerror|onload|onclick|onmouseover)=)|(%3Cscript%3E.*?%3C%2Fscript%3E)|((alert|prompt|confirm)\()|(<img.*?src=.*?onerror=.*?>)|(<svg.*?onload=.*?>)|((document\.cookie|document\.write|window\.location))",
        "target": "query_string",
    },
    "suspicious_user_agent": {
        "enabled": True,
        "pattern": r"(?:sqlmap|curl|wget|bot|crawler|scrapy|httpclient|nmap|nikto|fuzzer|burpsuite|zap|nessus|metasploit)",
        "target": "user_agent",
    },
    "path_traversal": {
        "enabled": True,
        "pattern": r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)|(/etc/passwd|/etc/shadow|/proc/self/environ|/windows/win.ini|/boot.ini|/etc/hosts)",
        "target": "query_string",
    },
    "rfi_lfi": {
        "enabled": True,
        "pattern": r"(http[s]?://|ftp://|file://)|(\.\./|\.\.\\)|(%2e%2e%2f)|(/etc/passwd|/proc/self/environ)",
        "target": "query_string",
    },
    "command_injection": {
        "enabled": True,
        "pattern": r"(;|\||&&|`|\$\(.*?\)|\{\{.*?\}\})|(\b(cat|ls|whoami|id|uname|rm|wget|curl|ping|nc|nmap)\b)",
        "target": "query_string",
    },
    "email_injection": {
        "enabled": True,
        "pattern": r"(\bBCC:|\bCC:|\bTO:)|(%0A|%0D|\\n|\\r)",
        "target": "query_string",
    },
    "http_header_injection": {
        "enabled": True,
        "pattern": r"(\r\n|\n|\r)(Set-Cookie:|Content-Length:|Location:|HTTP/1\.1)",
        "target": "query_string",
    },
    "csrf_token_missing": {
        "enabled": False,  # Disabled by default to avoid false positives
        "pattern": r"(?<!csrf_token=)[^&]*",
        "target": "query_string",
    },
}

# Default whitelist
DEFAULT_WHITELIST = {
    "query_string": [
        r"safe_param=value",
    ],
    "user_agent": [
        r"Mozilla/5.0.*",
        r"curl/.*",
        r"wget/.*",
    ],
}

# Active rules and whitelist (can be updated dynamically)
RULES = copy.deepcopy(DEFAULT_RULES)
WHITELIST = copy.deepcopy(DEFAULT_WHITELIST)

def load_user_config(user_rules=None, user_whitelist=None):
    global RULES, WHITELIST
    if user_rules:
        RULES.update(user_rules)
    if user_whitelist:
        for target, patterns in user_whitelist.items():
            WHITELIST.setdefault(target, []).extend(patterns)