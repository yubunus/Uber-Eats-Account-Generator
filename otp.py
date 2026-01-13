import imaplib
import email
import re
import asyncio
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
from email.message import Message
from datetime import datetime
import time


class IMAPClient:
    DEFAULT_PORTS = {
        'imap.gmail.com': 993
    }

    def __init__(self, username: str, password: str, server: str = None):
        self.username = username
        self.password = password
        self.server = server or 'imap.gmail.com'
        self.port = self.DEFAULT_PORTS.get(self.server, 993)
        self.connection = None

    def connect(self) -> bool:
        try:
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            self.connection.login(self.username, self.password)
            print(f"[✓] Connected to {self.server}")
            return True
        except imaplib.IMAP4.error as e:
            print(f"[✗] IMAP authentication failed: {e}")
            return False
        except Exception as e:
            print(f"[✗] Connection error: {e}")
            return False

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                print("[✓] Disconnected from IMAP server")
            except:
                pass

    def search_emails(self, criteria: List[Tuple[str, str]], folder: str = 'inbox') -> List[bytes]:
        if not self.connection:
            return []

        try:
            self.connection.select(folder)
            search_args = ['HEADER'] + [item for pair in criteria for item in pair]
            status, data = self.connection.search(None, *search_args)

            if status == 'OK' and data[0]:
                return data[0].split()
            return []
        except Exception as e:
            print(f"[✗] Email search failed: {e}")
            return []

    def fetch_email(self, email_id: bytes) -> Optional[Message]:
        if not self.connection:
            return None

        try:
            status, data = self.connection.fetch(email_id, '(RFC822)')

            if status == 'OK' and data[0]:
                return email.message_from_bytes(data[0][1])
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
        email_client: IMAPClient,
        target_email: str,
        service: str = 'uber',
        timeout: int = 60
    ) -> Optional[str]:
        if not email_client.connect():
            print("[✗] Failed to connect to email server")
            return None

        try:
            start_time = datetime.now()
            extractor = self.extractors.get(service, self.extractors['default'])

            while (datetime.now() - start_time).seconds < timeout:
                email_ids = email_client.search_emails([('To', target_email)])

                if email_ids:
                    latest_email_id = email_ids[-1]
                    msg = email_client.fetch_email(latest_email_id)

                    if msg:
                        otp = self._extract_otp_from_message(msg, extractor)
                        if otp:
                            print(f"[✓] Successfully extracted OTP: {otp}")
                            return otp

                time.sleep(2)

            print("[!] Timeout waiting for OTP email")
            return None
        except Exception as e:
            print(f"[✗] Error getting OTP: {e}")
            return None
        finally:
            email_client.disconnect()

    def _extract_otp_from_message(self, msg: Message, extractor: UberOTPExtractor) -> Optional[str]:
        try:
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == 'text/html':
                    html_content = part.get_payload(decode=True)
                    if html_content:
                        html_str = html_content.decode('utf-8', errors='ignore')
                        otp = extractor.extract(html_str)
                        if otp:
                            print(f"[✓] Found OTP in HTML: {otp}")
                            return otp

                elif content_type == 'text/plain':
                    text_content = part.get_payload(decode=True)
                    if text_content:
                        text_str = text_content.decode('utf-8', errors='ignore')
                        for pattern in UberOTPExtractor.OTP_PATTERNS:
                            match = re.search(pattern, text_str)
                            if match:
                                code = match.group(1) if match.lastindex else match.group(0)
                                if code.isdigit() and len(code) == 4:
                                    print(f"[✓] Found OTP in plain text: {code}")
                                    return code

            return None
        except Exception as e:
            print(f"[✗] Failed to extract OTP from message: {e}")
            return None

    async def get_otp_async(
        self,
        email_client: IMAPClient,
        target_email: str,
        service: str = 'uber',
        timeout: int = 60
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

# tests
# get last otp from from gmail in config
if __name__ == "__main__":
    import json
    import asyncio
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    imap_config = config.get('imap', {})
    
    if not imap_config.get('username') or not imap_config.get('password'):
        print("[!] IMAP credentials not found in config.json")
        exit(1)
    
    imap_client = IMAPClient(
        username=imap_config['username'],
        password=imap_config['password'],
        server=imap_config.get('server', 'imap.gmail.com')
    )
    
    print(f"[*] Connecting to {imap_config.get('server', 'imap.gmail.com')}...")
    
    if not imap_client.connect():
        print("[✗] Failed to connect to IMAP server")
        exit(1)
    
    try:
        imap_client.connection.select('inbox')
        
        status, data = imap_client.connection.search(None, 'SUBJECT', '"Welcome to Uber"')
        
        if status == 'OK' and data[0]:
            email_ids = data[0].split()
            if email_ids:
                latest_email_id = email_ids[-1]
                print(f"[*] Found {len(email_ids)} email(s) with subject 'Welcome to Uber'")
                print(f"[*] Extracting OTP from latest email...")
                
                msg = imap_client.fetch_email(latest_email_id)
                if msg:
                    extractor = UberOTPExtractor()
                    
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        
                        if content_type == 'text/html':
                            html_content = part.get_payload(decode=True)
                            if html_content:
                                html_str = html_content.decode('utf-8', errors='ignore')
                                otp = extractor.extract(html_str)
                                if otp:
                                    print(f"\n[✓] Found OTP: {otp}")
                                    break
                    else:
                        print(f"\n[!] No OTP found in email")
                else:
                    print(f"\n[!] Could not fetch email")
            else:
                print(f"\n[!] No emails found with subject 'Welcome to Uber'")
        else:
            print(f"\n[!] No emails found with subject 'Welcome to Uber'")
    
    finally:
        imap_client.disconnect()