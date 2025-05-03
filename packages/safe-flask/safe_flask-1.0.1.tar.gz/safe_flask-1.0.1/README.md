# FlaskGuard 🚀

FlaskGuard is a plug-and-play firewall library for Flask applications. It protects your application from common web vulnerabilities such as SQL injection, XSS, path traversal, and more.

## Features ✨

- 🔒 Detects and blocks malicious requests.
- ⚙️ Configurable rules and whitelist.
- 🛠️ Easy integration with Flask applications.
- 📜 Logging for blocked requests with color-coded output.
- 🧠 Advanced detection for SQL injection, XSS, path traversal, command injection, and more.

## Installation 🛠️

### From PyPI

Install FlaskGuard directly from PyPI:

```bash
pip install safe-flask
```

### From GitHub

Install FlaskGuard from the GitHub repository:

```bash
pip install git+https://github.com/username/FlaskGuard.git
```

### From Source

Clone the repository and install FlaskGuard locally:

```bash
git clone https://github.com/username/FlaskGuard.git
cd FlaskGuard
pip install .
```

## Usage 🚀

### Basic Integration

```python
from flask import Flask
from flask_guard import init_app

app = Flask(__name__)
init_app(app)

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
        "target": "query_string",
    }
}

custom_whitelist = {
    "query_string": [r"safe_custom_param=value"],
}

load_user_config(user_rules=custom_rules, user_whitelist=custom_whitelist)
```

## Rules 🛡️

FlaskGuard includes the following built-in rules:

1. **SQL Injection**: Detects SQL injection patterns such as `' OR 1=1`, `UNION SELECT`, `SLEEP()`, and more.
2. **XSS Attack**: Detects Cross-Site Scripting (XSS) patterns in `<script>` tags, event handlers, and encoded payloads.
3. **Suspicious User-Agent**: Blocks requests from tools commonly used in attacks, such as `sqlmap`, `curl`, `wget`, and more.
4. **Path Traversal**: Detects attempts to access sensitive files using patterns like `../../etc/passwd`.
5. **Remote and Local File Inclusion (RFI/LFI)**: Detects attempts to include remote or local files.
6. **Command Injection**: Detects shell command injection patterns and common commands like `ls`, `cat`, and `rm`.
7. **Email Injection**: Detects email header injection attempts using `BCC`, `CC`, and newline characters.
8. **HTTP Header Injection**: Detects HTTP header injection attempts with patterns like `Set-Cookie` and `Content-Length`.
9. **CSRF Token Missing**: Detects requests missing CSRF tokens.

## Testing the Firewall 🧪

You can test the firewall using `curl` commands. Below are examples of malicious requests:

### SQL Injection

```bash
curl "http://127.0.0.1:5000/malicious?query=%27%20OR%201%3D1%20--"
```

### XSS Attack

```bash
curl "http://127.0.0.1:5000/malicious?query=%3Cscript%3Ealert%281%29%3C%2Fscript%3E"
```

### Path Traversal

```bash
curl "http://127.0.0.1:5000/malicious?query=../../etc/passwd"
```

### Command Injection

```bash
curl "http://127.0.0.1:5000/malicious?query=ls%20-al"
```

### Email Injection

```bash
curl "http://127.0.0.1:5000/malicious?query=TO:%20victim@example.com%0ABCC:%20attacker@example.com"
```

### HTTP Header Injection

```bash
curl "http://127.0.0.1:5000/malicious?query=%0D%0ASet-Cookie:%20malicious=true"
```

### Legitimate Request

```bash
curl "http://127.0.0.1:5000/safe?query=safe_param=value"
```

## Contributing 🤝

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
