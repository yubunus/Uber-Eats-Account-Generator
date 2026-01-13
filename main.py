import json
import uuid
import random
import asyncio
import os
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from urllib.parse import quote

from engine.utils import RequestHandler
from engine.account_manager import AccountManager
from otp import EmailOTPExtractor, IMAPClient
from otp_hotmail import HotmailClient, EmailOTPExtractor as HotmailEmailOTPExtractor, BannedAccountException
from device import DeviceProfile


FIRST_NAMES = [
    "Alexander", "Emma", "Benjamin", "Olivia", "Samuel", "Sophia",
    "Nathan", "Isabella", "Ethan", "Mia", "Lucas", "Charlotte",
    "Mason", "Amelia", "Logan", "Harper", "Jacob", "Evelyn",
    "Owen", "Abigail", "Sebastian", "Emily", "Henry", "Ella"
]

LAST_NAMES = [
    "Campbell", "Mitchell", "Roberts", "Carter", "Phillips", "Evans",
    "Turner", "Torres", "Parker", "Collins", "Edwards", "Stewart",
    "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan",
    "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson"
]


class AccountGenerator:
    def __init__(self, config: dict = None, assigned_proxy: str = None):
        self.config = config or {}
        self.request_handler = RequestHandler(config, assigned_proxy=assigned_proxy)
        self.device = DeviceProfile(self.request_handler)

    async def get_session(self):
        self.request_handler.reset_session()

        # upsert device 1 task 
        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.device.drm_id,
            'x-uber-device': 'android',
            'x-uber-device-language': 'en_US',
            'user-agent': 'Cronet/129.0.6668.102@aa3a5623',
            'x-uber-device-os': self.device.os,
            'x-uber-device-sdk': self.device.sdk,
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-client-user-session-id': self.device.client_user_analytics_session_id,
            'x-uber-client-version': self.device.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.device.call_uuid,
            'x-uber-device-id': self.device.udid,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.device.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.device.app_variant,
            'x-uber-analytics-session-id': self.device.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'uberctx-client-network-request-uuid': self.device.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self.device._generate_epoch())),
            'uberctx-cold-launch-id': self.device.cold_launch_id,
            'x-uber-client-id': self.device.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.device.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            'request': {
                'installationID': self.device.installation_uuid,
                'clientType': 'android',
                'clientIntegrityToken': '',
            },
        }

        response = await self.request_handler.post('Upsert Device 1', "https://cn-geo1.uber.com/rt/devices/task", headers=headers, data=json_data)

        # upsert device 2 results
        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.device.drm_id,
            'x-uber-device': 'android',
            'x-uber-device-language': 'en_US',
            'user-agent': 'Cronet/129.0.6668.102@aa3a5623',
            'x-uber-device-os': self.device.os,
            'x-uber-device-sdk': self.device.sdk,
            'x-uber-request-uuid': self.device.client_network_request_uuid,
            'x-uber-client-user-session-id': self.device.client_user_analytics_session_id,
            'x-uber-client-version': self.device.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.device.call_uuid,
            'x-uber-device-id': self.device.udid,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.device.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.device.app_variant,
            'x-uber-analytics-session-id': self.device.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'x-uber-network-classifier': 'MEDIUM',
            'uberctx-client-network-request-uuid': self.device.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self.device._generate_epoch())),
            'uberctx-cold-launch-id': self.device.cold_launch_id,
            'x-uber-client-id': self.device.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.device.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            'request': {
                'installationID': self.device.installation_uuid,
                'msmAttestation': {
                    'token': self.device.generate_msm_attestation_token(),
                },
                'attemptNumber': 1,
            },
        }
        response = await self.request_handler.post('Upsert Device 2', "https://cn-geo1.uber.com/rt/devices/results", headers=headers, data=json_data)

        # upsert device 3 upsert
        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-device': 'android',
            'uber-trace-id': self.device.trace_id,
            'x-uber-device-language': 'en_US',
            'user-agent': self.device.user_agent,
            'x-uber-device-os': self.device.os,
            'x-uber-device-sdk': self.device.sdk,
            'x-uber-request-uuid': self.device.client_network_request_uuid,
            'x-uber-client-user-session-id': self.device.client_user_analytics_session_id,
            'x-uber-client-version': self.device.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.device.call_uuid,
            'x-uber-device-id': self.device.udid,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.device.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.device.app_variant,
            'x-uber-analytics-session-id': self.device.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'uberctx-client-network-request-uuid': self.device.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self.device._generate_epoch())),
            'uberctx-cold-launch-id': self.device.cold_launch_id,
            'x-uber-client-id': self.device.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.device.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            "deviceData": self.device.build_device_data_v2()
        }

        await self.request_handler.post(
            'Upsert Device 3',
            url="https://cn-geo1.uber.com/rt/devices/upsert",
            headers=headers,
            data=json_data
        )

        headers = {
            'sec-ch-ua': '"Chromium";v="142", "Android WebView";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'user-agent': self.device.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'x-uber-client-id': self.device.client_id,
            'x-uber-pwv-instance-id': str(uuid.uuid4()),
            'sec-ch-prefers-color-scheme': 'light',
            'x-uber-auth-social-login-providers': '["googleweb","google"]',
            'x-uber-device-data': self.device.build_device_data(),
            'x-uber-pwv-client-id': 'identity_eats_usl',
            'x-requested-with': self.device.client_id,
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
        }

        params = {
            'showDebugInfo': 'false',
            'x-uber-device': 'android',
            'x-uber-client-name': 'eats',
            'x-uber-client-version': self.device.version,
            'x-uber-client-id': self.device.client_id,
            'firstPartyClientID': self.device.first_party_client_id,
            'isEmbedded': 'true',
            'codeChallenge': self.device.pkce_challenge,
            'app_url': self.device.app_url,
            'asms': 'true',
            'x-uber-device-udid': self.device.udid,
            'sim_mcc': '',
            'sim_mnc': '',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-device-location-latitude': self.device.latitude,
            'x-uber-device-location-longitude': self.device.longitude,
            'socialNative': 'g',
            'x-uber-cold-launch-id': self.device.cold_launch_id,
            'x-uber-hot-launch-id': self.device.hot_launch_id,
            'x-uber-app-variant': self.device.app_variant,
            'countryCode': 'US',
            'known_user': 'false',
            'isChromeCustomTabSession': 'false',
        }

        referer_items = []
        for k, v in params.items():
            if k == 'app_url':
                referer_items.append(f"{k}={quote(str(v), safe='')}")
            else:
                referer_items.append(f"{k}={v}")
        referer_url = 'https://auth.uber.com/v2?' + '&'.join(referer_items)
        
        await self.request_handler.get("Get Session", "https://auth.uber.com/v2", headers=headers, params=params)

        # get udi-fingerprint
        headers = {
            'sec-ch-ua-platform': '"Android"',
            'x-csrf-token': 'x',
            'user-agent': self.device.user_agent,
            'sec-ch-ua': '"Android WebView";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'content-type': 'application/json',
            'sec-ch-ua-mobile': '?1',
            'accept': '*/*',
            'origin': 'https://auth.uber.com',
            'x-requested-with': self.device.client_id,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': referer_url,
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=1, i',
        }

        json_data = {
            'meta': self.device.get_device_fingerprint()
        }

        await self.request_handler.post('Get UDI Fingerprint', 'https://auth.uber.com/v2/udi-meta', headers=headers, data=json_data)

    async def email_signup(self, email: str) -> Optional[str]:
        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': '',
                'formAnswer': {
                    'flowType': 'INITIAL',
                    'standardFlow': True,
                    'accountManagementFlow': False,
                    'daffFlow': False,
                    'productConstraints': {
                        'autoSMSVerificationSupported': True,
                        'isEligibleForWebOTPAutofill': False,
                        'uslFELibVersion': '',
                        'uslMobileLibVersion': '',
                        'isWhatsAppAvailable': False,
                        'isPublicKeyCredentialSupported': True,
                        'isAppleAvailable': False,
                        'isFacebookAvailable': False,
                        'isGoogleAvailable': False,
                        'isRakutenAvailable': False,
                        'isKakaoAvailable': False,
                    },
                    'additionalParams': {
                        'isEmailUpdatePostAuth': False,
                    },
                    'deviceData': self.device.build_device_data(),
                    'codeChallenge': self.device.pkce_challenge,
                    'uslURL': self.device.build_usl_url(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'screenAnswers': [
                        {
                            'screenType': 'PHONE_NUMBER_INITIAL',
                            'eventType': 'TypeInputEmail',
                            'fieldAnswers': [
                                {
                                    'fieldType': 'EMAIL_ADDRESS',
                                    'emailAddress': email,
                                },
                            ],
                        },
                    ],
                    'appContext': {
                        'appUrl': self.device.app_url,
                        'socialNative': 'g',
                    },
                },
            },
        }
        
        headers = {
            'sec-ch-ua-platform': '"Android"',
            'x-uber-hot-launch-id': self.device.hot_launch_id,
            #'x-uber-challenge-provider': 'ARKOSE_TOKEN',
            'sec-ch-ua': '"Chromium";v="142", "Android WebView";v="142", "Not_A Brand";v="99"',
            'x-uber-device-location-longitude': self.device.longitude,
            'sec-ch-ua-mobile': '?1',
            'x-uber-client-name': 'eats',
            #'x-uber-challenge-token': '678187f84f1554b76.6387716002|r=us-west-2|meta=3|metabgclr=transparent|metaiconclr=%23757575|guitextcolor=%23000000|pk=30000F36-CADF-490C-929A-C6A7DD8B33C4|at=40|sup=1|rid=5|ag=101|cdn_url=https%3A%2F%2Fak04a6qc.uber.com%2Fcdn%2Ffc|surl=https%3A%2F%2Fak04a6qc.uber.com|smurl=https%3A%2F%2Fak04a6qc.uber.com%2Fcdn%2Ffc%2Fassets%2Fstyle-manager',
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-app-variant': self.device.app_variant,
            'content-type': 'application/json',
            'x-uber-device': 'android',
            'x-csrf-token': 'x',
            'x-uber-cold-launch-id': self.device.cold_launch_id,
            'x-uber-device-udid': self.device.udid,
            'accept-language': 'en',
            'x-uber-usl-id': self.device.udid,
            'x-uber-device-location-latitude': self.device.latitude,
            'x-uber-client-version': self.device.version,
            'user-agent': self.device.user_agent,
            'x-uber-client-id': self.device.client_id,
            'accept': '*/*',
            'origin': 'https://auth.uber.com',
            'x-requested-with': self.device.client_id,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.device.build_usl_url(),
            'priority': 'u=1, i',
        }

        """
        cookies = {
            '_cc': 'AcWQI%2FVRsGGasJLDQCpGie66',
            '_cid_cc': 'AcWQI%2FVRsGGasJLDQCpGie66',
            '_ua': '{"session_id":"fa153bf6-1425-4700-8fb4-02184a87655b","session_time_ms":1764711506103}',
            'udi-fingerprint': 'w5UnWL+SLhGOkmgubZD3/XEuAMKnY1hRi3yWdikE6fooNmc2eYNB5HwiQdtsq9O+Jl0k2d88Q4+HxbN6VZDYuQ==7BaOiGUaoSFvcz4lYOw82P1owRIhjr6psRVQGPVt5DA=',
        }
        """

        response = await self.request_handler.post(
            "Email Signup",
            "https://auth.uber.com/v2/submit-form",
            headers,
            json_data
        )

        if response:
            try:
                if not response.text or response.text.strip() == '':
                    print(f"[!] Email Signup: Empty response body")
                    return None
                return response.json().get('inAuthSessionID')
            except json.JSONDecodeError as e:
                print(f"[!] Email Signup: Invalid JSON response - {e}")
                print(f"    Response text: {response.text[:200]}")
                return None
        return None

    async def submit_otp(self, session_id: str, otp: str) -> Optional[Dict[str, Any]]:
        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': session_id,
                'formAnswer': {
                    'flowType': 'SIGN_UP',
                    'standardFlow': True,
                    'accountManagementFlow': False,
                    'daffFlow': False,
                    'productConstraints': {
                        'autoSMSVerificationSupported': True,
                        'isEligibleForWebOTPAutofill': False,
                        'uslFELibVersion': '',
                        'uslMobileLibVersion': '',
                        'isWhatsAppAvailable': False,
                        'isPublicKeyCredentialSupported': False,
                        'isAppleAvailable': False,
                        'isFacebookAvailable': False,
                        'isGoogleAvailable': False,
                        'isRakutenAvailable': False,
                        'isKakaoAvailable': False,
                        'isGoogleDeeplinkAvailable': True,
                    },
                    'additionalParams': {
                        'isEmailUpdatePostAuth': False,
                    },
                    'deviceData': self.device.build_device_data(),
                    'codeChallenge': self.device.pkce_challenge,
                    'uslURL': self.device.build_usl_url(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'screenAnswers': [
                        {
                            'screenType': 'EMAIL_OTP_CODE',
                            'eventType': 'TypeEmailOTP',
                            'fieldAnswers': [
                                {
                                    'fieldType': 'EMAIL_OTP_CODE',
                                    'emailOTPCode': otp,
                                },
                            ],
                        },
                    ],
                },
            },
        }

        headers = {
            'X-Uber-Usl-Id': self.device.udid,
            'X-Uber-Hot-Launch-Id': self.device.hot_launch_id,
            'x-uber-device-location-latitude': self.device.latitude,
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'Accept-Language': 'en',
            'X-Uber-Device-Udid': self.device.udid,
            'X-Uber-Client-Name': 'eats',
            'X-Uber-Device': 'android',
            'X-Uber-Client-Version': self.device.version,
            'X-Uber-App-Variant': self.device.app_variant,
            'X-Uber-Cold-Launch-Id': self.device.cold_launch_id,
            'X-Uber-Client-Id': self.device.client_id,
            'User-Agent': self.device.user_agent,
            'Content-Type': 'application/json',
            'X-Uber-App-Device-Id': self.device.app_device_id,
            'x-uber-device-location-longitude': self.device.longitude,
            'Accept': '*/*',
            'Origin': 'https://auth.uber.com',
            'X-Requested-With': self.device.client_id,
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://auth.uber.com/',
        }

        response = await self.request_handler.post(
            "Submit OTP",
            "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
            headers,
            json_data
        )

        if response:
            return response.json()
        return None

    async def _skip_phone_number(self, session_id: str) -> Optional[str]:
        """
        Function: Skip phone number screen
        On signup, some times submit_otp results in the next step being PHONE_NUMBER_PROGRESSIVE, rather than FULL_NAME_PROGRESSIVE.
        To handle this, only on these cases do we call _skip_phone_number to handle this phone number screen issue.
        """

        headers = {
            'X-Uber-Usl-Id': self.device.udid,
            'X-Uber-Hot-Launch-Id': self.device.hot_launch_id,
            'X-Uber-Device-Location-Latitude': self.device.latitude,
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'Accept-Language': 'en',
            'X-Uber-Device-Udid': self.device.udid,
            'X-Uber-Client-Name': 'eats',
            'X-Uber-Device': 'android',
            'X-Uber-Client-Version': self.device.version,
            'X-Uber-App-Variant': self.device.app_variant,
            'X-Uber-Cold-Launch-Id': self.device.cold_launch_id,
            'X-Uber-Client-Id': self.device.client_id,
            'User-Agent': self.device.user_agent,
            'Content-Type': 'application/json',
            'X-Uber-App-Device-Id': self.device.app_device_id,
            'X-Uber-Device-Location-Longitude': self.device.longitude,
            'Accept': '*/*',
            'Origin': 'https://auth.uber.com',
            'X-Requested-With': self.device.client_id,
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://auth.uber.com/',
        }

        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': session_id,
                'formAnswer': {
                    'flowType': 'PROGRESSIVE_SIGN_UP',
                    'standardFlow': True,
                    'accountManagementFlow': False,
                    'daffFlow': False,
                    'productConstraints': {
                        'autoSMSVerificationSupported': True,
                        'isEligibleForWebOTPAutofill': False,
                        'uslFELibVersion': '',
                        'uslMobileLibVersion': '',
                        'isWhatsAppAvailable': False,
                        'isPublicKeyCredentialSupported': False,
                        'isAppleAvailable': False,
                        'isFacebookAvailable': False,
                        'isGoogleAvailable': False,
                        'isRakutenAvailable': False,
                        'isKakaoAvailable': False,
                        'isGoogleDeeplinkAvailable': True,
                    },
                    'additionalParams': {
                        'isEmailUpdatePostAuth': False,
                    },
                    'deviceData': self.device.build_device_data(),
                    'codeChallenge': self.device.pkce_challenge,
                    'uslURL': self.device.build_usl_url(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'screenAnswers': [
                        {
                            'screenType': 'SKIP',
                            'eventType': 'TypeSkip',
                            'fieldAnswers': [],
                        },
                    ],
                },
            },
        }

        response = await self.request_handler.post(
            "Skip Phone Number",
            "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
            headers,
            json_data
        )

        if response:
            return response.json().get('inAuthSessionID')
        return None

    async def _submit_name(self, session_id: str, name: str) -> Optional[str]:
        first_name, last_name = name.split(' ', 1)

        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': session_id,
                'formAnswer': {
                    'flowType': 'PROGRESSIVE_SIGN_UP',
                    'standardFlow': True,
                    'accountManagementFlow': False,
                    'daffFlow': False,
                    'productConstraints': {
                        'autoSMSVerificationSupported': True,
                        'isEligibleForWebOTPAutofill': False,
                        'uslFELibVersion': '',
                        'uslMobileLibVersion': '',
                        'isWhatsAppAvailable': False,
                        'isPublicKeyCredentialSupported': False,
                        'isAppleAvailable': False,
                        'isFacebookAvailable': False,
                        'isGoogleAvailable': False,
                        'isRakutenAvailable': False,
                        'isKakaoAvailable': False,
                        'isGoogleDeeplinkAvailable': True,
                    },
                    'additionalParams': {
                        'isEmailUpdatePostAuth': False,
                    },
                    'deviceData': self.device.build_device_data(),
                    'uslURL': self.device.build_usl_url(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'screenAnswers': [
                        {
                            'screenType': 'FULL_NAME_PROGRESSIVE',
                            'eventType': 'TypeInputNewUserFullName',
                            'fieldAnswers': [
                                {
                                    'fieldType': 'FIRST_NAME',
                                    'firstName': first_name,
                                },
                                {
                                    'fieldType': 'LAST_NAME',
                                    'lastName': last_name,
                                },
                            ],
                        },
                    ],
                },
            },
        }

        headers = {
            'X-Uber-Usl-Id': self.device.udid,
            'X-Uber-Hot-Launch-Id': self.device.hot_launch_id,
            'x-uber-device-location-longitude': self.device.latitude,
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'Accept-Language': 'en',
            'X-Uber-Device-Udid': self.device.udid,
            'X-Uber-Client-Name': 'eats',
            'X-Uber-Device': 'android',
            'X-Uber-Client-Version': self.device.version,
            'X-Uber-App-Variant': self.device.app_variant,
            'X-Uber-Cold-Launch-Id': self.device.cold_launch_id,
            'X-Uber-Client-Id': self.device.client_id,
            'User-Agent': self.device.user_agent,
            'Content-Type': 'application/json',
            'X-Uber-App-Device-Id': self.device.app_device_id,
            'x-uber-device-location-longitude': self.device.longitude,
            'Accept': '*/*',
            'Origin': 'https://auth.uber.com',
            'X-Requested-With': self.device.client_id,
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://auth.uber.com/',
        }

        response = await self.request_handler.post(
            "Submit Name",
            "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
            headers,
            json_data
        )

        if response:
            return response.json().get('inAuthSessionID')
        return None

    async def _submit_legal_confirmation(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': session_id,
                'formAnswer': {
                    'flowType': 'SIGN_UP',
                    'standardFlow': True,
                    'accountManagementFlow': False,
                    'daffFlow': False,
                    'productConstraints': {
                        'autoSMSVerificationSupported': True,
                        'isEligibleForWebOTPAutofill': False,
                        'uslFELibVersion': '',
                        'uslMobileLibVersion': '',
                        'isWhatsAppAvailable': False,
                        'isPublicKeyCredentialSupported': False,
                        'isAppleAvailable': False,
                        'isFacebookAvailable': False,
                        'isGoogleAvailable': False,
                        'isRakutenAvailable': False,
                        'isKakaoAvailable': False,
                        'isGoogleDeeplinkAvailable': True,
                    },
                    'additionalParams': {
                        'isEmailUpdatePostAuth': False,
                    },
                    'deviceData': self.device.build_device_data(),
                    'uslURL': self.device.build_usl_url(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'screenAnswers': [
                        {
                            'screenType': 'LEGAL',
                            'eventType': 'TypeSignupLegal',
                            'fieldAnswers': [
                                {
                                    'fieldType': 'LEGAL_CONFIRMATION',
                                    'legalConfirmation': True,
                                },
                                {
                                    'fieldType': 'LEGAL_CONFIRMATIONS',
                                    'legalConfirmations': {
                                        'legalConfirmations': [
                                            {
                                                'disclosureVersionUUID': 'ef1d61c9-b09e-4d44-8cfb-ddfa15cc7523',
                                                'isAccepted': True,
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    ],
                },
            },
        }

        headers = {
            'X-Uber-Usl-Id': self.device.udid,
            'X-Uber-Hot-Launch-Id': self.device.hot_launch_id,
            'x-uber-device-location-latitude': self.device.latitude,
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'Accept-Language': 'en',
            'X-Uber-Device-Udid': self.device.udid,
            'X-Uber-Client-Name': 'eats',
            'X-Uber-Device': 'android',
            'X-Uber-Client-Version': self.device.version,
            'X-Uber-App-Variant': self.device.app_variant,
            'X-Uber-Cold-Launch-Id': self.device.cold_launch_id,
            'X-Uber-Client-Id': self.device.client_id,
            'User-Agent': self.device.user_agent,
            'Content-Type': 'application/json',
            'X-Uber-App-Device-Id': self.device.app_device_id,
            'x-uber-device-location-longitude': self.device.longitude,
            'Accept': '*/*',
            'Origin': 'https://auth.uber.com',
            'X-Requested-With': self.device.client_id,
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://auth.uber.com/',
        }

        response = await self.request_handler.post(
            "Submit Legal",
            "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
            headers,
            json_data
        )

        if response:
            resp_json = response.json()
            try:
                fields = resp_json.get('form', {}).get('screens', [{}])[0].get('fields', [])
                auth_code = fields[0].get('authCode') if fields else None
                session_id = resp_json.get('inAuthSessionID')
                return session_id, auth_code
            except (IndexError, KeyError):
                print("[!] Failed to extract auth code")
                return None, None

        return None, None

    async def _submit_auth_code(self, session_id: str, auth_code: str, email: str = '', name: str = '') -> Tuple[bool, Optional[dict]]:
        json_data = {
            'formContainerAnswer': {
                'inAuthSessionID': f'{session_id}.{auth_code}',
                'formAnswer': {
                    'flowType': 'SIGN_IN',
                    'screenAnswers': [
                        {
                            'screenType': 'SESSION_VERIFICATION',
                            'fieldAnswers': [
                                {
                                    'fieldType': 'SESSION_VERIFICATION_CODE',
                                    'sessionVerificationCode': auth_code,
                                },
                                {
                                    'fieldType': 'CODE_VERIFIER',
                                    'codeVerifier': self.device.pkce_verifier,
                                },
                            ],
                            'eventType': 'TypeVerifySession',
                        },
                    ],
                    'deviceData': self.device.build_device_data(),
                    'firstPartyClientID': self.device.first_party_client_id,
                    'standardFlow': True,
                    'appID': 'EATS',
                },
            },
        }

        headers = {
            'X-Uber-Device-Mobile-Iso2': self.device.location_country,
            'X-Uber-Drm-Id': self.device.drm_id,
            'X-Uber-Device': 'android',
            'X-Uber-Cit': self.device.build_cit_token(),
            'X-Uber-Device-Language': f'en_{self.device.location_country}',
            'User-Agent': 'Cronet/129.0.6668.102@aa3a5623',
            'X-Uber-Device-Os': self.device.os,
            'X-Uber-Device-Sdk': self.device.sdk,
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'X-Uber-Client-User-Session-Id': self.device.client_user_analytics_session_id,
            'X-Uber-Client-Version': self.device.version,
            'X-Uber-Device-Manufacturer': 'Google',
            'X-Uber-Call-Uuid': str(uuid.uuid4()),
            'X-Uber-Device-Id': self.device.udid,
            'X-Uber-Markup-Textformat-Version': '1',
            'X-Uber-Device-Model': self.device.model,
            'Uberctx-Mobile-Initiated': 'true',
            'X-Uber-App-Variant': self.device.app_variant,
            'X-Uber-Analytics-Session-Id': self.device.client_user_analytics_session_id,
            'X-Uber-Sig-Params': 'a=ES256;v=1',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Uber-Network-Classifier': 'MEDIUM',
            'Uberctx-Client-Network-Request-Uuid': str(uuid.uuid4()),
            'X-Uber-Device-Epoch': str(int(self.device._generate_epoch())),
            'Uberctx-Cold-Launch-Id': self.device.cold_launch_id,
            'X-Uber-Client-Id': self.device.client_id,
            'X-Uber-App-Lifecycle-State': 'foreground',
            'X-Uber-Protocol-Version': '0.73.0',
            'X-Uber-Device-Timezone': self.device.location_city,
            'X-Uber-Client-Name': 'eats', # stays as eats even for postmates
            'X-Uber-Client-Session': str(uuid.uuid4()),
            'X-Uber-Device-Time-24-Format-Enabled': '0',
            'X-Uber-App-Device-Id': self.device.app_device_id,
            'X-Uber-Device-Voiceover': '0',
            'Priority': 'u=1, i',
        }
        headers['X-Uber-Sig'] = self.device.build_sig_token(headers)

        response = await self.request_handler.post(
            "Submit Auth Code",
            "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
            headers,
            json_data
        )

        if response:
            resp_json = response.json()
            return True, resp_json
        else:
            return False, None
    
    async def finish_signup(self, auth_code):
        # get user id token
        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.device.drm_id,
            'x-uber-device': 'android',
            'x-uber-device-language': 'en_US',
            'user-agent': 'Cronet/129.0.6668.102@aa3a5623',
            'authorization': f'Bearer {auth_code}',
            'x-uber-device-os': self.device.os,
            'x-uber-device-sdk': self.device.sdk,
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-client-user-session-id': self.device.client_user_analytics_session_id,
            'x-uber-client-version': self.device.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.device.call_uuid,
            'x-uber-device-id': self.device.udid,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.device.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.device.app_variant,
            'x-uber-analytics-session-id': self.device.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'x-uber-network-classifier': 'MEDIUM',
            'x-uber-token': 'no-token',
            'uberctx-client-network-request-uuid': self.device.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self.device._generate_epoch())),
            'uberctx-cold-launch-id': self.device.cold_launch_id,
            'x-uber-client-id': self.device.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.device.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            'request': {
                'clientID': self.device.first_party_client_id,
                'skipSigning': True,
            },
        }

        await self.request_handler.post('get cookie id token', 'https://cn-geo1.uber.com/rt/identity/oauth2/user-id-token', headers=headers, data=json_data)


        # GSU
        device_data_header = json.loads(self.device.build_device_data())
        headers = {
            'sec-ch-ua': '"Android WebView";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'user-agent': self.device.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.device.drm_id,
            'x-uber-device': 'android',
            'x-uber-cold-launch-id': self.device.cold_launch_id,
            'sec-ch-prefers-color-scheme': 'light',
            'x-uber-device-language': 'en_US',
            'x-uber-device-os': self.device.os,
            'x-uber-device-sdk': self.device.sdk,
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-client-version': self.device.version,
            'x-uber-client-user-session-id': self.device.client_user_analytics_session_id,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-device-id': self.device.udid,
            'x-uber-hot-launch-id': self.device.hot_launch_id,
            'x-uber-device-model': self.device.model,
            'x-uber-app-variant': self.device.app_variant,
            'x-uber-device-data': device_data_header,
            'x-uber-device-udid': self.device.udid,
            'x-uber-device-epoch': str(int(self.device.device_epoch)),
            'x-uber-client-id': self.device.client_id,
            'x-uber-device-timezone': self.device.location_city,
            'x-uber-pwv-instance-id': str(uuid.uuid4()),
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.device.client_session_uuid,
            'x-uber-pwv-client-id': 'identity_eats_uam',
            'x-uber-app-device-id': self.device.app_device_id,
            'x-requested-with': self.device.client_id,
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
        }

        params = [
            ('entry_ctx', 'usl_email_first_signup_optional'),
            ('entry_domain', 'auth.uber.com'),
            ('type', '11'),
            ('host_theme', 'light'),
            ('type', '11'),
        ]

        await self.request_handler.get('GSU', 'https://account.uber.com/gsu', headers=headers, params=params)

    async def create_account_hotmail(self, hotmail_account: str, hotmail_client_key: str, sleep: int = 5, apply_promo: bool = False) -> Optional[dict]:
        """Create account using Hotmail for OTP verification"""
        await self.device.initialize()

        with open('config.json', 'r') as f:
            config = json.load(f)

        parts = hotmail_account.split(':')
        if len(parts) < 4:
            print("[!] Invalid hotmail account format. Expected: email:password:token:uuid")
            return None

        hotmail_email = parts[0]

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"

        print(f"\n[*] Creating account using hotmail: {hotmail_email}")
        await self.get_session()

        await asyncio.sleep(sleep)

        session_id = await self.email_signup(hotmail_email)
        if not session_id:
            print("[!] Failed to initiate signup")
            return None

        print("[*] Waiting for OTP...")
        await asyncio.sleep(sleep)

        try:
            hotmail_client = HotmailClient(
                account=hotmail_account,
                client_key=hotmail_client_key
            )

            otp_extractor = HotmailEmailOTPExtractor()
            otp = await otp_extractor.get_otp_async(
                email_client=hotmail_client,
                target_email=hotmail_email,
                service='uber',
                timeout=60
            )

            if not otp:
                print("[!] Failed to retrieve OTP")
                return None
        except BannedAccountException as e:
            print(f"[!] Hotmail account is banned: {e}")
            return None
        except Exception as e:
            print(f"[!] Error getting OTP: {e}")
            return None

        print(f"[✓] OTP received: {otp}")

        # Submit OTP
        response = await self.submit_otp(session_id, otp)
        flow_type = response.get('form', {}).get('screens', [{}])[0].get('screenType', '')
        session_id = response.get('inAuthSessionID', None)
        if not session_id:
            print("[!] Failed to verify OTP")
            return None

        await asyncio.sleep(sleep)

        # if flow is phone number progressive, trigger skip phone number function
        if flow_type == 'PHONE_NUMBER_PROGRESSIVE':
            session_id = await self._skip_phone_number(session_id)
            if not session_id:
                print("[!] Failed to skip phone number")
                return None

        # Submit name
        session_id = await self._submit_name(session_id, name)
        if not session_id:
            print("[!] Failed to submit name")
            return None

        await asyncio.sleep(sleep)

        # Submit legal confirmation
        session_id, auth_code = await self._submit_legal_confirmation(session_id)
        if not session_id or not auth_code:
            print("[!] Failed to submit legal confirmation")
            return None

        await asyncio.sleep(sleep)

        # Submit auth code and get final response
        success, resp_json = await self._submit_auth_code(session_id, auth_code, hotmail_email, name)
        if not success:
            print("[!] Failed to complete registration")
            return None

        # set cookies
        self.cookies = resp_json['cookies']
        for cookie in resp_json["cookies"]:
            self.request_handler.session.cookies.set(
                name=cookie["name"],
                value=cookie["value"],
                domain=cookie["domain"],
                path=cookie.get("path", "/"),
                secure=True
            )

        # get necessary data
        self.auth_token = resp_json['oAuthInfo']['accessToken']
        self.refresh_token = resp_json['oAuthInfo']['refreshToken']
        self.sid = resp_json['cookies'][0]['value']
        self.user_uuid = resp_json['userUUID']

        await self.finish_signup(self.auth_token)

        self.account_manager = AccountManager(self.request_handler, self.device, self.sid, self.auth_token, self.user_uuid)

        if apply_promo:
            await self.account_manager.apply_promo(config['promos']['promo_code'])

        print("[✓] Account created successfully!")

        return resp_json, flow_type

    async def create_account(self, email: str, imap_config: dict, sleep: int = 5, apply_promo: bool = False) -> Optional[dict]:
        await self.device.initialize()

        with open('config.json', 'r') as f:
            config = json.load(f)   

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"

        print(f"\n[*] Creating account for: {email}")
        await self.get_session()

        await asyncio.sleep(sleep)

        session_id = await self.email_signup(email)
        if not session_id:
            print("[!] Failed to initiate signup")
            return None

        print("[*] Waiting for OTP...")
        await asyncio.sleep(sleep)

        try:
            imap_client = IMAPClient(
                username=imap_config['username'],
                password=imap_config['password'],
                server=imap_config.get('server', 'imap.gmail.com')
            )
            
            otp_extractor = EmailOTPExtractor()
            otp = await otp_extractor.get_otp_async(imap_client, email, timeout=60)

            if not otp:
                print("[!] Failed to retrieve OTP")
                return None
        except Exception as e:
            print(f"[!] Error getting OTP: {e}")
            return None

        print(f"[✓] OTP received: {otp}")

        # Submit OTP
        response = await self.submit_otp(session_id, otp)
        flow_type = response.get('form', {}).get('screens', [{}])[0].get('screenType', '')
        session_id = response.get('inAuthSessionID', None)
        if not session_id:
            print("[!] Failed to verify OTP")
            return None

        await asyncio.sleep(sleep)

        # if flow is phone number progressive, trigger skip phone number function
        if flow_type == 'PHONE_NUMBER_PROGRESSIVE':
            session_id = await self._skip_phone_number(session_id)
            if not session_id:
                print("[!] Failed to skip phone number")
                return None

        # Submit name
        session_id = await self._submit_name(session_id, name)
        if not session_id:
            print("[!] Failed to submit name")
            return None

        await asyncio.sleep(sleep)

        # Submit legal confirmation
        session_id, auth_code = await self._submit_legal_confirmation(session_id)
        if not session_id or not auth_code:
            print("[!] Failed to submit legal confirmation")
            return None

        await asyncio.sleep(sleep)

        # Submit auth code and get final response
        success, resp_json = await self._submit_auth_code(session_id, auth_code, email, name)
        if not success:
            print("[!] Failed to complete registration")
            return None


        # set cookies
        self.cookies = resp_json['cookies']
        for cookie in resp_json["cookies"]:
            self.request_handler.session.cookies.set(
                name=cookie["name"],
                value=cookie["value"],
                domain=cookie["domain"],
                path=cookie.get("path", "/"),
                secure=True
            )

        # get necessary data
        self.auth_token = resp_json['oAuthInfo']['accessToken']
        self.refresh_token = resp_json['oAuthInfo']['refreshToken']
        self.sid = resp_json['cookies'][0]['value']
        self.user_uuid = resp_json['userUUID']

        await self.finish_signup(self.auth_token)

        self.account_manager = AccountManager(self.request_handler, self.device, self.sid, self.auth_token, self.user_uuid)

        if apply_promo:
            await self.account_manager.apply_promo(config['promos']['promo_code'])

        print("[✓] Account created successfully!")
        
        return resp_json, flow_type

async def process_single_hotmail_account(config: dict, idx: int, total: int, proxies_list: list, hotmail_accounts: list) -> dict:
    if not hotmail_accounts:
        print("[!] No hotmail accounts available")
        return {
            'success': False,
            'email': 'N/A',
            'error': 'No hotmail accounts available'
        }

    hotmail_account = hotmail_accounts.pop(0)
    hotmail_email = hotmail_account.split(':')[0]

    try:
        hotmail_file = 'hotmail_accounts.txt'
        if os.path.exists(hotmail_file):
            with open(hotmail_file, 'r') as f:
                lines = f.readlines()

            with open(hotmail_file, 'w') as f:
                for line in lines:
                    if line.strip() != hotmail_account:
                        f.write(line)

            print(f"[✓] Removed {hotmail_email} from {hotmail_file}")
    except Exception as e:
        print(f"[!] Warning: Failed to remove account from file: {e}")

    print(f"\n{'='*60}")
    print(f"[*] Processing account {idx}/{total} using hotmail: {hotmail_email}")
    print(f"{'='*60}")

    assigned_proxy = None
    if config.get('proxies_enabled', False) and proxies_list:
        if len(proxies_list) > 0:
            assigned_proxy = proxies_list.pop(random.randint(0, len(proxies_list) - 1))
            print(f"[*] Assigned proxy to account {idx}: {assigned_proxy[:30]}...")
            RequestHandler.remove_proxy_from_file(assigned_proxy)
        else:
            print(f"[!] No proxies left for account {idx}, proceeding without proxy")

    generator = AccountGenerator(config, assigned_proxy=assigned_proxy)
    hotmail_client_key = config.get('hotmail_client_key', '')

    if not hotmail_client_key:
        print("[!] hotmail_client_key not found in config.json")
        return {
            'success': False,
            'email': hotmail_email,
            'error': 'hotmail_client_key not configured'
        }

    try:
        # Step 1: Create account using hotmail
        response, flow_type = await generator.create_account_hotmail(
            hotmail_account,
            hotmail_client_key,
            sleep=config.get('sleep', 5),
            apply_promo=config['promos']['apply_promo']
        )

        if not response:
            print(f"[!] Failed to create account using hotmail: {hotmail_email}")
            return {
                'success': False,
                'email': hotmail_email,
                'error': 'Account creation failed'
            }

        # Save Details
        result_email = response.get('userProfile', {}).get('email', hotmail_email)
        print(f"[✓] Successfully created Uber account for: {result_email}")
        account_info = {
            'email': result_email,
            'hotmail_account': hotmail_account,
            'flow_type': flow_type,
            'timezone': generator.device.location_city,
            'longitude': generator.device.longitude,
            'latitude': generator.device.latitude,
            'model': generator.device.model,
            'phone_name': generator.device.phone_name,
            'brand': generator.device.brand,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # save local data
        if config.get('app_variant') == 'ubereats':
            with open('genned/genned_accounts.json', 'r+') as f:
                data = json.load(f)
                data['accounts'].append(account_info)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
        elif config.get('app_variant') == 'postmates':
            with open('genned/postmates_genned.json', 'r+') as f:
                data = json.load(f)
                data['accounts'].append(account_info)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

        # save data for production
        account_info['auth_token'] = generator.auth_token
        account_info['refresh_token'] = generator.refresh_token
        account_info['cookies'] = generator.cookies

        with open('genned/genned_accounts_production.json', 'r+') as f:
            data = json.load(f)
            data['accounts'].append(account_info)
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

        return {
            'success': True,
            'email': result_email,
            'hotmail_account': hotmail_account,
            'error': None
        }
    except Exception as e:
        print(f"[!] Error processing {hotmail_email}: {e}")
        return {
            'success': False,
            'email': hotmail_email,
            'error': str(e)
        }


async def process_single_account(config: dict, idx: int, total: int, proxies_list: list) -> dict:
    imap_config = config.get('imap', {})
    domains = imap_config.get('domains', [])
    
    if not domains:
        print("[!] No domains configured in config.json")
        return {
            'success': False,
            'email': 'N/A',
            'account_line': 'N/A',
            'error': 'No domains configured'
        }
    
    domain = random.choice(domains)
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email = f"{first_name.lower()}{last_name.lower()}{random.randint(1000, 9999)}@{domain}"
    
    print(f"\n{'='*60}")
    print(f"[*] Processing account {idx}/{total}: {email}")
    print(f"{'='*60}")
    
    assigned_proxy = None
    if config.get('proxies_enabled', False) and proxies_list:
        if len(proxies_list) > 0:
            assigned_proxy = proxies_list.pop(random.randint(0, len(proxies_list) - 1))
            print(f"[*] Assigned proxy to account {idx}: {assigned_proxy[:30]}...")
            RequestHandler.remove_proxy_from_file(assigned_proxy)
        else:
            print(f"[!] No proxies left for account {idx}, proceeding without proxy")

    generator = AccountGenerator(config, assigned_proxy=assigned_proxy)
    
    try:
        # Step 1: Create account
        response, flow_type = await generator.create_account(email, imap_config, sleep=config.get('sleep', 5), apply_promo=config['promos']['apply_promo'])
        
        if not response:
            print(f"[!] Failed to create account for: {email}")
            return {
                'success': False,
                'email': email,
                'error': 'Account creation failed'
            }
        
        # Save Details
        result_email = response.get('userProfile', {}).get('email', email)
        print(f"[✓] Successfully created Uber account for: {result_email}")
        account_info = {
            'email': result_email,
            'flow_type': flow_type,
            'timezone': generator.device.location_city,
            'longitude': generator.device.longitude,
            'latitude': generator.device.latitude,
            'model': generator.device.model,
            'phone_name': generator.device.phone_name,
            'brand': generator.device.brand,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # save local data
        with open('genned_accounts.json', 'r+') as f:
            data = json.load(f)
            data['accounts'].append(account_info)
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

        # save data for production
        account_info['auth_token'] = generator.auth_token
        account_info['refresh_token'] = generator.refresh_token
        account_info['cookies'] = generator.cookies

        with open('genned_accounts_production.json', 'r+') as f:
            data = json.load(f)
            data['accounts'].append(account_info)
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        
        return {
            'success': True,
            'email': result_email,
            'error': None
        }
    except Exception as e:
        print(f"[!] Error processing {email}: {e}")
        return {
            'success': False,
            'email': email,
            'error': str(e)
        }


async def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    print("\n" + "="*60)
    print("Account Type Selection")
    print("="*60)
    print("1. Catchall (using IMAP)")
    print("2. Hotmail (using hotmail accounts)")
    print("="*60)

    account_type = input("Select account type (1 or 2): ").strip()

    if account_type not in ['1', '2']:
        print("[!] Invalid selection. Please choose 1 or 2.")
        return

    use_hotmail = (account_type == '2')

    hotmail_accounts = []
    if use_hotmail:
        if not config.get('hotmail_client_key'):
            print("[!] hotmail_client_key not found in config.json")
            return

        hotmail_file = 'hotmail_accounts.txt'
        if not os.path.exists(hotmail_file):
            print(f"[!] {hotmail_file} not found")
            print(f"[!] Please create {hotmail_file} with hotmail accounts (one per line)")
            print(f"[!] Format: email:password:token:uuid")
            return

        with open(hotmail_file, 'r') as f:
            hotmail_accounts = [line.strip() for line in f.readlines() if line.strip()]

        if not hotmail_accounts:
            print(f"[!] No hotmail accounts found in {hotmail_file}")
            return

        print(f"[✓] Loaded {len(hotmail_accounts)} hotmail accounts")
    else:
        if 'imap' not in config:
            print("[!] IMAP configuration not found in config.json")
            return

        imap_config = config['imap']
        if not all(key in imap_config for key in ['username', 'password', 'domains']):
            print("[!] IMAP configuration incomplete. Need username, password, and domains.")
            return

        if not imap_config['domains']:
            print("[!] No domains configured in imap.domains")
            return
    
    proxies_list = []
    if config.get('proxies_enabled', False):
        proxies_list = RequestHandler.load_proxies()
        if proxies_list:
            print(f'[✓] Loaded {len(proxies_list)} proxies from proxies.txt')
        else:
            print('[!] Proxies enabled but none loaded, proceeding without proxies')
            config['proxies_enabled'] = False
    
    num_of_accounts_to_generate = input("Enter number of accounts to generate: ")

    try:
        num_of_accounts_to_generate = int(num_of_accounts_to_generate)
        if num_of_accounts_to_generate <= 0:
            print("[!] Invalid number. Must be greater than 0.")
            return
    except ValueError:
        print("[!] Invalid input. Please enter a number.")
        return

    if use_hotmail and num_of_accounts_to_generate > len(hotmail_accounts):
        print(f"[!] Warning: Only {len(hotmail_accounts)} hotmail accounts available for {num_of_accounts_to_generate} requested")
        print(f"[!] Will generate {len(hotmail_accounts)} accounts")
        num_of_accounts_to_generate = len(hotmail_accounts)

    print(f"[*] Generating {num_of_accounts_to_generate} accounts")

    if config.get('proxies_enabled', False):
        if len(proxies_list) < num_of_accounts_to_generate:
            print(f"[!] Warning: Only {len(proxies_list)} proxies available for {num_of_accounts_to_generate} accounts")
            print(f"[!] Some accounts will be created without proxies")

    print("[*] Starting account generation...\n")

    # Process accounts in batches of 20
    batch_size = 20
    all_results = []

    for batch_start in range(0, num_of_accounts_to_generate, batch_size):
        batch_end = min(batch_start + batch_size, num_of_accounts_to_generate)
        batch_num = (batch_start // batch_size) + 1
        total_batches = (num_of_accounts_to_generate + batch_size - 1) // batch_size

        print(f"\n{'='*60}")
        print(f"[*] Processing Batch {batch_num}/{total_batches} (Accounts {batch_start + 1}-{batch_end})")
        print(f"{'='*60}\n")

        # Create tasks for this batch
        if use_hotmail:
            tasks = [
                process_single_hotmail_account(config, idx, num_of_accounts_to_generate, proxies_list, hotmail_accounts)
                for idx in range(batch_start + 1, batch_end + 1)
            ]
        else:
            tasks = [
                process_single_account(config, idx, num_of_accounts_to_generate, proxies_list)
                for idx in range(batch_start + 1, batch_end + 1)
            ]

        print(f"[*] Running {len(tasks)} account creation tasks in parallel for this batch...")
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        all_results.extend(batch_results)

        print(f"\n[✓] Batch {batch_num}/{total_batches} completed")
        print(f"[*] {len([r for r in batch_results if isinstance(r, dict) and r.get('success')])} successful in this batch")
    
    successful_accounts = []
    failed_accounts = []
    
    # Summary
    print(f"\n{'='*60}")
    print("[*] Account Generation Summary")
    print(f"{'='*60}")
    print(f"[✓] Successful: {len(successful_accounts)}")
    print(f"[✗] Failed: {len(failed_accounts)}")
    
    if successful_accounts:
        print("\n[✓] Successfully created accounts:")
        for acc in successful_accounts:
            print(f"  - {acc}")
    
    if failed_accounts:
        print("\n[✗] Failed accounts:")
        for acc in failed_accounts:
            print(f"  - {acc}")

if __name__ == '__main__':
    asyncio.run(main())
