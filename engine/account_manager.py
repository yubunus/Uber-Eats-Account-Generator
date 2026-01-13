import uuid
from device import DeviceProfile
from engine.utils import RequestHandler
import asyncio

class AccountManager:
    def __init__(self, request_handler: RequestHandler, device_manager: DeviceProfile, sid: str, auth_token: str, user_uuid: str):
        self.request_handler = request_handler
        self.device = device_manager
        self.sid = sid
        self.auth_token = auth_token
        self.user_uuid = user_uuid

    async def change_password(self, new_password: str):
        headers = {
            'x-uber-identity-entrypoint': 'uam',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Chromium";v="142", "Android WebView";v="142", "Not_A Brand";v="99"',
            'x-uber-device-location-longitude': self.device.longitude,
            'sec-ch-ua-mobile': '?1',
            'x-uber-client-name': 'eats',
            'x-uber-marketing-id': str(uuid.uuid4()),
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-app-device-id': self.device.app_device_id,
            #'x-uber-infrasec': '0b32ff200030061d:____ibR_Q__4T30PU_Z_S___NW__O6_______cd__Ktu__________j_',
            'x-uber-app-variant': self.device.app_variant,
            'content-type': 'application/json',
            #'x-uber-edge-tls-ja3-fingerprint': '5659c10619c455ea477287b12cf3f7e7',
            'x-uber-device-id': self.device.udid,
            'x-uber-device': 'android',
            'x-csrf-token': 'x',
            'x-uber-device-language': f'en_{self.device.location_country}',
            'x-uber-device-udid': self.device.udid,
            'x-uber-device-model': self.device.model,
            'x-uber-device-os': self.device.os,
            #'x-uber-edge-botdefense': '842a052ee1c4ecc8a1a6051656e35864:0119d74b7888e3371a206e7ed758e31e32aec0b38f3b2182158d3771b2bbae793de902134e5135aa17b45f29f9e9a4c675f4cc9f0a3ac425a7ddc7a23fa7ec61728d57190fab6bfe1a0c5e7e86634d7ccb95a7eb693c326d5e93b3c1:0:get',
            'x-uber-device-location-latitude': '0',
            'x-uber-client-version': self.device.version,
            'x-uber-device-mobile-iso2': self.device.location_country,
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-client-id': self.device.client_id,
            #'x-uber-auth-sso-id': '0538fecc-3cf9-464c-96d2-1b44578e4cf3',
            'user-agent': self.device.user_agent,
            'accept': '*/*',
            'origin': 'https://account.uber.com',
            'x-requested-with': self.device.client_id,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.uber.com/workflow?host_theme=light&workflow_next_url=BACK&workflow=PASSWORD',
            'accept-language': f'en-{self.device.location_country},en;q=0.9',
            'priority': 'u=1, i',
        }

        json_data = {
            'currentScreen': 'PASSWORD',
            'workflowId': {
                'value': 'identity_factor.collect_password',
            },
            'sessionId': {
                'uuid': {
                    'value': '',
                },
            },
            'event': {
                'eventType': 'EVENT_TYPE_ENTER_PASSWORD',
                'enterPassword': {
                    'password': new_password,
                    'cookieSid': self.sid
                },
            },
        }

        response = await self.request_handler.post(
            'Change Password',
            'https://account.uber.com/api/passwordWorkflow?localeCode=en',
            headers=headers,
            data=json_data,
        )
        
        if response:
            print(f'[✓] Password changed successfully')
            return response.json()
        else:
            print(f'[✗] Failed to change password')
            return None

    
    async def apply_promo(self, promo_code: str):
        """
        Apply promo to account using web api
        its better to apply using mobile api because thats what this is based on, ill probably add that in the future but its like this for now

        reason for that is because im missing a pre requisite to the mobile api call which results in 401, maybe apply address, upsert device, or the /target-promotion 401 call
        didnt have time to look into that more so i just added this, still works so i didnt feel like changing it
        """
        headers = {
            'user-agent': self.device.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'origin': 'https://www.ubereats.com',
            'referer': 'https://www.ubereats.com',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=1, i',
        }
        # get web cookies
        await self.request_handler.get('Get Cookies home', 'https://www.ubereats.com', headers=headers)
        await self.request_handler.get('Get SID Cookies', 'https://www.ubereats.com/login-redirect/', headers=headers)

        headers['x-csrf-token'] = 'x'
        headers['content-type'] = 'application/json'
        # maybe session id

        # apply promo
        response = await self.request_handler.post('Add Promo', 'https://www.ubereats.com/_p/api/applyPromoV1', headers=headers, data={'code': promo_code})
        await asyncio.sleep(1)
        response = await self.request_handler.post('Get Promos', 'https://www.ubereats.com/_p/api/getSavingsV1', headers=headers, data={'type': 'ACCOUNT'})
        if response:
            try:
                for promo_json in response.json()['data']['promoManagerSections'][0]['promoManagerItems']:
                    self.promotion_name = promo_json['savingItem']['saving']['presentationData']['title']
                    print(f"[✓] Promotion: {self.promotion_name}")
            except:
                print("[!] No promotion found")