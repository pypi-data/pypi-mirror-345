# sqlproxy

**sqlproxy** is a Python CLI tool to automate login attempts with a fixed password using usernames fetched from a GitHub file. It also sets the Windows system proxy to route traffic through Burp Suite (127.0.0.1:8080).

### ?? Features

- Sets and resets Windows proxy settings
- Fetches usernames from a remote URL
- Sends login requests through Burp Suite
- Waits for `Ctrl + K` to exit and restore settings

### ?? Installation

```bash
pip install sqlproxy
