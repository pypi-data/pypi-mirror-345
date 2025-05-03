# FlaskGuard 🚀

FlaskGuard is a plug-and-play firewall library for Flask applications. It protects your application from common web vulnerabilities such as SQL injection, XSS, path traversal, and more.

## Features ✨

- 🔒 Detects and blocks malicious requests in both query strings and POST request bodies.
- ⚙️ Configurable multi-target rules and whitelist.
- 🛠️ Easy integration with Flask applications.
- 📜 Logging for blocked requests with color-coded output, including details about the source of malicious input.
- 🧠 Advanced detection for SQL injection, XSS, path traversal, command injection, and more.
- 🛡️ Customizable blocked responses for enhanced flexibility.
- 🚀 **Now with POST request support**: Analyze and block malicious patterns in POST request bodies.
- 🧪 **Experimental JSON Injection Protection**: Disabled by default, can be enabled for testing.

## Installation 🛠️

### From PyPI

Install FlaskGuard directly with Pip:

```bash
pip install safe-flask
```

### From GitHub

Install FlaskGuard from the GitHub repository:

```bash
pip install git+https://github.com/CodeGuardianSOF/FlaskGuard.git
```

### From Source

Clone the repository and install FlaskGuard locally:

```bash
git clone https://github.com/CodeGuardianSOF/FlaskGuard.git
cd FlaskGuard
pip install .
```

## Usage 🚀

### Basic Integration

```python
from flask import Flask
from flask_guard import FlaskGuard

app = Flask(__name__)
FlaskGuard(app)

@app.route("/")
def home():
    return "Welcome to FlaskGuard-protected app!"

if __name__ == "__main__":
    app.run()
```

### Custom Rules and Whitelist

```python
from flask_guard.rules import load_user_config

custom_rules = {
    "custom_rule": {
        "enabled": True,
        "pattern": r"custom_pattern",
        "target": ["query_string", "post_body"],  # Apply to both query strings and POST bodies
    }
}

custom_whitelist = {
    "query_string": [r"safe_custom_param=value"],
    "post_body": [r"safe_post_param=value"],
}

load_user_config(user_rules=custom_rules, user_whitelist=custom_whitelist)
```

### Custom Blocked Response

You can customize the response returned when a request or response is blocked by FlaskGuard:

```python
def custom_blocked_response():
    return '403 Forbidden', [b"Custom Firewall Blocked Message: Access Denied."]

FlaskGuard(app, custom_blocked_response=custom_blocked_response)
```

## Rules 🛡️

FlaskGuard includes the following built-in rules:

1. **SQL Injection**: Detects SQL injection patterns such as `' OR 1=1`, `UNION SELECT`, `SLEEP()`, and more. Applies to both query strings and POST bodies.
2. **XSS Attack**: Detects Cross-Site Scripting (XSS) patterns in `<script>` tags, event handlers, and encoded payloads. Applies to both query strings and POST bodies.
3. **Suspicious User-Agent**: Blocks requests from tools commonly used in attacks, such as `sqlmap`, `curl`, `wget`, `python-requests`, and more.
4. **Path Traversal**: Detects attempts to access sensitive files using patterns like `../../etc/passwd`. Applies to both query strings and POST bodies.
5. **Remote and Local File Inclusion (RFI/LFI)**: Detects attempts to include remote or local files. Applies to both query strings and POST bodies.
6. **Command Injection**: Detects shell command injection patterns and common commands like `ls`, `cat`, `rm`, `bash`, and `powershell`. Applies to both query strings and POST bodies.
7. **Email Injection**: Detects email header injection attempts using `BCC`, `CC`, and newline characters. Applies to both query strings and POST bodies.
8. **HTTP Header Injection**: Detects HTTP header injection attempts with patterns like `Set-Cookie` and `Content-Length`. Applies to both query strings and POST bodies.
9. **Directory Listing**: Detects responses exposing directory listings, such as `Index of /`. Applies to response bodies.
10. **Open Redirect**: Detects potential open redirect vulnerabilities in query strings.
11. **JSON Injection (Experimental)**: Detects malicious patterns in JSON payloads, such as `__proto__`, `constructor`, and `<script>`. **Disabled by default** and applies only to POST bodies.

## Testing the Firewall 🧪

You can test the firewall using `curl` commands. Below are examples of malicious requests:

### SQL Injection

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=' OR 1=1 --"
```

### XSS Attack

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=<script>alert(1)</script>"
```

### Path Traversal

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=../../etc/passwd"
```

### Command Injection

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=ls -al"
```

### Email Injection

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=TO: victim@example.com\nBCC: attacker@example.com"
```

### HTTP Header Injection

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=\r\nSet-Cookie: malicious=true"
```

### Directory Listing

```bash
curl -X GET "http://127.0.0.1:5000/malicious"
```

### Open Redirect

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -d "query=http://malicious-site.com"
```

### JSON Injection (Experimental)

```bash
curl -X POST "http://127.0.0.1:5000/malicious" -H "Content-Type: application/json" -d '{"__proto__": "malicious"}'
```

### Legitimate Request

```bash
curl -X POST "http://127.0.0.1:5000/safe" -d "query=safe_param=value"
```

## Contributing 🤝

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
