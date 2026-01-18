from curl_cffi import requests, CurlHttpVersion
import requests as req
from typing import Optional, Dict, List
import json
import random
import asyncio


class RequestHandler:
    def __init__(self, config: Dict = None, assigned_proxy: str = None):
        self.session = requests.Session()
        self.proxies_enabled = False
        self.current_proxy = None

        if config:
            self.proxies_enabled = config.get('proxies_enabled', False)
            if self.proxies_enabled and assigned_proxy:
                self.current_proxy = assigned_proxy
                self.session.proxies = {
                    'http': assigned_proxy,
                    'https': assigned_proxy
                }
                print(f'[✓] Using assigned proxy: {assigned_proxy[:20]}...')
            elif self.proxies_enabled and not assigned_proxy:
                print('[!] Proxies enabled but no proxy assigned')
                self.proxies_enabled = False
    
    @staticmethod
    def load_proxies() -> List[str]:
        try:
            with open('proxies.txt', 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            proxies = []
            for line in lines:
                proxy = RequestHandler._parse_proxy_static(line)
                if proxy:
                    proxies.append(proxy)

            return proxies
        except FileNotFoundError:
            print('[!] proxies.txt not found')
            return []
        except Exception as e:
            print(f'[!] Error loading proxies: {e}')
            return []

    @staticmethod
    def remove_proxy_from_file(proxy_to_remove: str):
        try:
            with open('proxies.txt', 'r') as f:
                lines = f.readlines()

            # Filter out the proxy that was used
            remaining_lines = []
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    parsed = RequestHandler._parse_proxy_static(line.strip())
                    if parsed != proxy_to_remove:
                        remaining_lines.append(line)
                else:
                    remaining_lines.append(line)

            with open('proxies.txt', 'w') as f:
                f.writelines(remaining_lines)

            print(f'[✓] Removed proxy from proxies.txt')
        except Exception as e:
            print(f'[!] Error removing proxy from file: {e}')
    
    @staticmethod
    def _parse_proxy_static(proxy_string: str) -> Optional[str]:
        """Format proxies - handles various formats"""
        # Handle proxies that already have http:// or https:// prefix
        if proxy_string.startswith('http://') or proxy_string.startswith('https://'):
            protocol = 'https://' if proxy_string.startswith('https://') else 'http://'
            remaining = proxy_string[len(protocol):]

            if '@' in remaining:
                return proxy_string

            parts = remaining.split(':')

            if len(parts) == 2:
                return proxy_string

            elif len(parts) == 4:
                host, port, user, password = parts
                return f'{protocol}{user}:{password}@{host}:{port}'

            else:
                print(f'[!] Could not parse proxy format with protocol: {proxy_string}')
                return None

        if '@' in proxy_string:
            auth, location = proxy_string.split('@', 1)
            return f'http://{auth}@{location}'

        parts = proxy_string.split(':')

        if len(parts) == 2:
            ip, port = parts
            return f'http://{ip}:{port}'

        elif len(parts) == 4:
            first_looks_like_ip = '.' in parts[0] or parts[0].replace('.', '').isdigit()

            if first_looks_like_ip:
                ip, port, user, password = parts
                return f'http://{user}:{password}@{ip}:{port}'
            else:
                user, password, ip, port = parts
                return f'http://{user}:{password}@{ip}:{port}'

        print(f'[!] Could not parse proxy format: {proxy_string}')
        return None

    def reset_session(self):
        self.session.close()
        self.session = requests.Session()
        if self.proxies_enabled and self.current_proxy:
            self.session.proxies = {
                'http': self.current_proxy,
                'https': self.current_proxy
            }

    async def _get_ip_info(self):
        response = await self.get("Get Proxy Information", "http://ip-api.com/json/")
        if response:
            return response.json()
        return None

    async def get(self, name: str, url: str, headers: Dict=None, params: Dict=None) -> Optional[requests.Response]:
        try:
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10,
                    impersonate='chrome116',
                    )
            except:
                print("Trying http1...")
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30,
                    impersonate='chrome116',
                    http_version=CurlHttpVersion.V1_1,
                    )

            if response.status_code == 200:
                print(f'[✓] {name} request successful')
                return response
            else:
                print(f'[✗] {name} failed: {response.status_code}')
                print(f'    Response: {response.text[:200]}...')
                return None

        except Exception as e:
            print(f"[!] Request error in {name}: {e}")
            return None

    async def post(self, name: str, url: str, headers: Dict, data: Dict) -> Optional[requests.Response]:
        try:
            # try curl cffi default request, if fails then switch to http1. some proxies dont support higher level http hence this block
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    data=json.dumps(data, separators=(",", ":")),
                    timeout=10,
                    impersonate='chrome116',
                )
            except:
                print("Trying http1...")
                response = self.session.post(
                    url,
                    headers=headers,
                    data=json.dumps(data, separators=(",", ":")),
                    timeout=30,
                    impersonate='chrome116',
                    http_version=CurlHttpVersion.V1_1,
                )

            if response.status_code == 200 or (response.status_code == 204 and name == 'Get UDI Fingerprint'):
                print(f'[✓] {name} request successful')
                return response
            else:
                print(f'[✗] {name} failed: {response.status_code}')
                print(f'    Response: {response.text[:200]}...')
                return None

        except Exception as e:
            print(f"[!] Request error in {name}: {e}")
            return None
        