import re
import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime
import time
import requests
import json
import os


class BannedAccountException(Exception):
    # when hotmail acc is banned. todo implementation
    pass


class HotmailClient:
    def __init__(self, account: str, client_key: str):
        self.account = account
        self.client_key = client_key
        self.api_base = "https://gapi.hotmail007.com/v1/mail"
        self.full_account_string = None

    def remove_from_file(self, filepath: str = 'hotmail_accs.txt'):
        try:
            if not os.path.exists(filepath):
                return

            with open(filepath, 'r') as f:
                lines = f.readlines()

            email = self.account.split(':')[0] if ':' in self.account else self.account
            filtered_lines = [line for line in lines if not line.startswith(email)]

            with open(filepath, 'w') as f:
                f.writelines(filtered_lines)

            print(f"[!] Removed banned account from {filepath}")
        except Exception as e:
            print(f"[✗] Failed to remove account from file: {e}")

    def _handle_ban_if_needed(self, data: dict):
        # Check if account is banned/compromised
        if data.get('code') == 1:
            error_msg = data.get('message', '')
            if 'AADSTS70000' in error_msg or 'compromised' in error_msg.lower() or 'invalid_grant' in error_msg:
                print(f"[✗] BANNED ACCOUNT DETECTED: {self.account.split(':')[0]}")
                print(f"[!] Account is flagged as compromised by Microsoft")
                self.remove_from_file()
                raise BannedAccountException(f"Account {self.account.split(':')[0]} is banned/compromised")

    def _fetch_first_mail(self, folder: str) -> Optional[dict]:
        url = f"{self.api_base}/getFirstMail"
        params = {
            'clientKey': self.client_key,
            'account': self.account,
            'folder': folder
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"[✗] API request failed ({folder}): {response.status_code}")
            print(f"[✗] Response: {response.text[:200]}")
            return None

        data = response.json()
        if data.get('success') and data.get('code') == 0:
            email_data = data.get('data')
            return email_data if email_data else None

        self._handle_ban_if_needed(data)

        if data.get('code') != 0:
            print(f"[✗] API returned error ({folder}): {data}")
        return None

    def _parse_email_ts(self, email_data: dict) -> Optional[float]:
        if not email_data:
            return None

        for k in ('timestamp', 'time', 'Time', 'date', 'Date', 'receivedAt', 'ReceivedAt', 'receiveTime', 'ReceiveTime'):
            v = email_data.get(k)
            if v is None:
                continue
            try:
                # already numeric (epoch seconds or ms)
                if isinstance(v, (int, float)):
                    # treat very large values as ms
                    return (float(v) / 1000.0) if float(v) > 1e12 else float(v)
                if isinstance(v, str) and v.strip().isdigit():
                    num = float(v.strip())
                    return (num / 1000.0) if num > 1e12 else num
            except Exception:
                pass

        for k in ('DateTime', 'datetime', 'DateTimeUtc', 'dateTime', 'received', 'Received', 'receivedDateTime', 'ReceivedDateTime'):
            v = email_data.get(k)
            if not v:
                continue
            try:
                s = str(v).strip().replace('Z', '+00:00')
                dt = datetime.fromisoformat(s)
                return dt.timestamp()
            except Exception:
                pass

        return None

    def get_latest_email(self, folder: str = 'both') -> Optional[dict]:
        """
        folder:
          - 'inbox' -> only inbox
          - 'junkemail' -> only junk
          - 'both' -> fetch both and return whichever is newest (best-effort by timestamp)
        """
        try:
            folder = (folder or 'both').lower()

            if folder in ('inbox', 'junkemail'):
                return self._fetch_first_mail(folder)

            # default: check BOTH
            inbox_email = self._fetch_first_mail('inbox')
            junk_email = self._fetch_first_mail('junkemail')

            if not inbox_email and not junk_email:
                return None
            if inbox_email and not junk_email:
                return inbox_email
            if junk_email and not inbox_email:
                return junk_email

            inbox_ts = self._parse_email_ts(inbox_email)
            junk_ts = self._parse_email_ts(junk_email)

            # pick newest email from timestamp
            if inbox_ts is not None and junk_ts is not None:
                return inbox_email if inbox_ts >= junk_ts else junk_email

            return inbox_email

        except BannedAccountException:
            raise
        except requests.exceptions.Timeout:
            print(f"[!] Request timed out - API is slow, retrying...")
            return None
        except Exception as e:
            print(f"[✗] Failed to fetch email: {e}")
            return None


class UberOTPExtractor:
    OTP_PATTERNS = [
        r'\b\d{4}\b',
        r'verification code[:\s]+(\d{4})',
        r'code[:\s]+(\d{4})',
        r'>\s*(\d{4})\s*<'
    ]

    def extract(self, html_content: str) -> Optional[str]:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            otp_element = soup.find('td', class_='p1b')
            if otp_element:
                text = otp_element.get_text(strip=True)
                if text.isdigit() and len(text) == 4:
                    return text

            otp_element = soup.find('td', class_='p2b')
            if otp_element:
                text = otp_element.get_text(strip=True)
                if text.isdigit() and len(text) == 4:
                    return text

            verification_elements = soup.find_all(string=re.compile(r'verification code', re.I))
            for element in verification_elements:
                if element.parent:
                    parent = element.parent
                    for sibling in parent.find_next_siblings():
                        if sibling.name:
                            text = sibling.get_text(strip=True)
                            if text.isdigit() and len(text) == 4:
                                return text

                    if parent.parent:
                        grandparent = parent.parent
                        for sibling in grandparent.find_next_siblings():
                            if sibling.name:
                                digit_elements = sibling.find_all(string=re.compile(r'\b\d{4}\b'))
                                for digit_element in digit_elements:
                                    text = digit_element.strip()
                                    if text.isdigit() and len(text) == 4:
                                        return text

            bold_elements = soup.find_all(['b', 'strong']) + soup.find_all('td', class_=re.compile(r'bold|p1b|p2b'))
            for element in bold_elements:
                text = element.get_text(strip=True)
                if text.isdigit() and len(text) == 4:
                    return text

            white_boxes = soup.find_all('td', style=re.compile(r'background-color:\s*#ffffff', re.I))
            for box in white_boxes:
                text = box.get_text(strip=True)
                if text.isdigit() and len(text) == 4:
                    return text
                for pattern in self.OTP_PATTERNS:
                    match = re.search(pattern, str(box))
                    if match:
                        code = match.group(1) if match.lastindex else match.group(0)
                        if code.isdigit() and len(code) == 4:
                            return code

            text_content = soup.get_text()
            four_digit_numbers = re.findall(r'\b\d{4}\b', text_content)
            for number in four_digit_numbers:
                if number not in ['2024', '2025', '2023', '2022', '1999', '2000', '2026']:
                    return number

            return None
        except Exception as e:
            print(f"[✗] OTP extraction failed: {e}")
            return None


class EmailOTPExtractor:
    def __init__(self):
        self.extractors = {
            'uber': UberOTPExtractor(),
            'default': UberOTPExtractor()
        }

    def get_otp_from_email(
        self,
        email_client: HotmailClient,
        target_email: str,
        service: str = 'uber',
        timeout: int = 15
    ) -> Optional[str]:
        try:
            start_time = datetime.now()
            extractor = self.extractors.get(service, self.extractors['default'])
            attempt = 0

            while (datetime.now() - start_time).seconds < timeout:
                attempt += 1
                if attempt > 1 and attempt % 5 == 0:
                    print(f"[*] Still waiting for OTP... (attempt {attempt})")

                with open('config.json', 'r') as f:
                    _ = json.load(f).get('folder', 'inbox')

                email_data = email_client.get_latest_email('both')

                if email_data:
                    html_content = email_data.get('Html') or email_data.get('html') or email_data.get('content') or ''
                    text_content = email_data.get('Text') or email_data.get('text') or email_data.get('body') or ''
                    subject = email_data.get('subject', '')

                    skip_subjects = [
                        'New app(s) connected to your Microsoft account',
                        'Microsoft account',
                        'Security alert',
                        'Verification code for Microsoft'
                    ]

                    should_skip = any(skip_text.lower() in subject.lower() for skip_text in skip_subjects)

                    if should_skip:
                        print(f"[*] Skipping non-Uber email: {subject[:50]}...")
                        time.sleep(2)
                        continue

                    if attempt == 1 and (html_content or text_content):
                        print(f"[*] Found email with subject: {subject[:50]}...")

                    if html_content:
                        otp = extractor.extract(html_content)
                        if otp:
                            print(f"[✓] Successfully extracted OTP: {otp}")
                            return otp

                    if text_content:
                        for pattern in UberOTPExtractor.OTP_PATTERNS:
                            match = re.search(pattern, text_content)
                            if match:
                                code = match.group(1) if match.lastindex else match.group(0)
                                if code.isdigit() and len(code) == 4:
                                    print(f"[✓] Found OTP in text: {code}")
                                    return code

                wait_time = min(2 + (attempt // 3), 5)
                time.sleep(wait_time)

            print("[!] Timeout waiting for OTP email")
            return None
        except Exception as e:
            print(f"[✗] Error getting OTP: {e}")
            return None

    async def get_otp_async(
        self,
        email_client: HotmailClient,
        target_email: str,
        service: str = 'uber',
        timeout: int = 15
    ) -> Optional[str]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.get_otp_from_email,
            email_client,
            target_email,
            service,
            timeout
        )


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    print("Options:")
    print("1. Use last generated hotmail account")
    print("2. Enter account manually (full format: email:password:token:uuid)")
    choice = input("Choice (1 or 2): ").strip()

    if choice == "1":
        with open('genned/genned_accounts.json', 'r') as f:
            gjson = json.load(f)
        if not gjson:
            print("[!] No accounts found in genned_accounts.json")
            exit(1)
        account = gjson['accounts'][-1]['hotmail_account']
        print(f"[*] Using last generated account")
    else:
        print("\nEnter FULL account string (email:password:token:uuid)")
        account = input('Account: ').strip()

    if not account or ':' not in account:
        print("[!] Invalid account format. Must be: email:password:token:uuid")
        exit(1)

    email = account.split(':')[0]

    email_client = HotmailClient(
        account=account,
        client_key=config['hotmail_client_key']
    )

    extractor = EmailOTPExtractor()

    print(f"[*] Checking for OTP sent to: {email}")
    print("[*] Waiting for OTP (timeout: 15 seconds)...")

    otp = extractor.get_otp_from_email(
        email_client=email_client,
        target_email=email,
        service='uber',
        timeout=15
    )

    if otp:
        print(f"[✓] OTP Retrieved: {otp}")
    else:
        print("[!] Failed to retrieve OTP")
