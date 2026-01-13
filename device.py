import os
import json
import uuid
import time
import hashlib
from typing import Dict, Tuple
import random
from curl_cffi import requests

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import secrets
from spoof import Pixel9ProSpoof, CCJS_TOKEN, CCJS_TAG, xor_base64_utf8

from engine.utils import RequestHandler

def base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


class DeviceProfile:
    def __init__(self, request_handler: RequestHandler = None):
        self.read_config()
        self.request_handler = request_handler if request_handler else RequestHandler()

        # App specifics
        self.first_party_client_id = 'S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z'
        if self.config['app_variant'] == 'postmates':
            self.version = '6.299.10001'
            self.client_id = 'com.postmates.android'
            self.app_variant = 'postmates'
            self.app_url = f'uberlogin://auth3.uber.com/applogin/postmates'
            self.version_checksum = '50bd155c2f4fd6a9d6031196a40b80a0'
        elif self.config['app_variant'] == 'ubereats':
            self.version = '6.299.10001'
            self.client_id = 'com.ubercab.eats'
            self.app_variant = 'ubereats'
            self.app_url = f'uberlogin://auth3.uber.com/applogin/eats'
            self.version_checksum = '2f2a44b9b3f33da81dadfec899e4954a'
        else:
            raise ValueError(f"Invalid app variant: {self.config['app_variant']}")

        # Device Specifics
        self.user_agent = self.device_json['user_agent']
        self.os = self.device_json['os_latest']
        self.sdk = '35'
        self.brand = self.device_json['brand']
        self.model = self.device_json['model']
        self.location_city = None  # Will be set in initialize
        self.location_country = 'US'
        self.device_width = self.device_json['width']
        self.device_height = self.device_json['height']
        self.cpu_abi = self.device_json['cpuAbi']
        self.latitude = None  # Will be set in initialize
        self.longitude = None  # Will be set in initialize

        # for testing(not used)
        self.phone_name = self.device_json['phone_name']

        self.udid = str(uuid.uuid4())
        self.app_device_id = str(uuid.uuid4())
        self.cold_launch_id = str(uuid.uuid4())
        self.hot_launch_id = str(uuid.uuid4())
        self.client_user_analytics_session_id = str(uuid.uuid4())
        self.call_uuid = str(uuid.uuid4())
        self.client_network_request_uuid = str(uuid.uuid4())
        self.client_session_uuid = str(uuid.uuid4())

        self.android_id = secrets.token_hex(8)
        self.google_advertising_id = str(uuid.uuid4())
        self.google_app_set_id = str(uuid.uuid4())
        self.installation_uuid = str(uuid.uuid4())
        self.drm_id = secrets.token_hex(32).upper()
        self.device_id = hashlib.md5(self.android_id.encode()).hexdigest()


        self.ip_address = f"192.168.1.{random.randint(1, 254)}"
        self.device_epoch = int(time.time() * 1000)
        self.pkce_verifier, self.pkce_challenge = self._generate_pkce()
        self.trace_id = self._generate_trace_id()

    async def initialize(self):
        ip_info = await self.request_handler._get_ip_info()
        if ip_info:
            self.location_city = ip_info.get('timezone', 'America/Los_Angeles')
            self.latitude = str(ip_info.get('lat', 0.0))
            self.longitude = str(ip_info.get('lon', 0.0))
            print(f'[✓] Device location set: {self.location_city} ({self.latitude}, {self.longitude})')
        else:
            # Fallback values if IP info fails
            self.location_city = 'America/Los_Angeles'
            self.latitude = '0.0'
            self.longitude = '0.0'
            print(f'[!] Failed to get IP info, using fallback location')

    def read_config(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)
        with open("devices.json", "r") as f:
            tem = json.load(f)
            self.device_json = random.choice(tem['devices'])

    def generate_uber_session(self, session_id: str, session_duration_ms: int = 1800000) -> str:
        now_ms = int(time.time() * 1000)

        inner_session = {
            "session_id": {
                "uuid": {
                    "value": session_id
                }
            },
            "expires_at": {"value": now_ms + session_duration_ms},
            "created_at": {"value": now_ms}
        }

        inner_b64 = base64.b64encode(
            json.dumps(inner_session, separators=(',', ':')).encode()
        ).decode()

        user_session_b64 = base64.b64encode(inner_b64.encode()).decode()

        outer_session = {
            "user_session": user_session_b64,
            "cookie_expires_at": {"value": now_ms + 10000},  # +10 sec
            "cookie_created_at": {"value": now_ms},
            "action": 2
        }

        tem = base64.b64encode(
            json.dumps(outer_session, separators=(',', ':')).encode()
        ).decode()
        tem = tem[:-2]
        return tem

    def _generate_pkce(self) -> Tuple[str, str]:
        verifier = base64url(os.urandom(32))
        while len(verifier) != 43:
            verifier = base64url(os.urandom(32))
        challenge = base64url(hashlib.sha256(verifier.encode()).digest())
        return verifier, challenge

    def _generate_perf_id(self) -> str:
        install_uuid = self.installation_uuid.replace('-', '')
        timestamp_seconds = int(time.time())
        combined = f"{install_uuid}{timestamp_seconds}{self.android_id}"
        sha1_hash = hashlib.sha1(combined.encode()).hexdigest()[:32]
        return f"{sha1_hash[0:8]}-{sha1_hash[8:12]}-{sha1_hash[12:16]}-{sha1_hash[16:20]}-{sha1_hash[20:32]}".upper()
    
    def _generate_trace_id(self) -> str:
        trace_id = secrets.token_hex(16)
        span_id = secrets.token_hex(8)
        parent_span_id = "0"
        flags = "0"

        return f"{trace_id}:{span_id}:{parent_span_id}:{flags}"

    def _generate_epoch(self) -> float:
        return time.time() * 1000

    def build_device_data_v2(self) -> str:
        epoch_ms = int(self._generate_epoch())
        session_start_ms = epoch_ms - random.randint(1000, 5000)
        foreground_start_ms = session_start_ms + random.randint(500, 2000)
        
        data = {
            "data": {
                "dimensions": {
                    "android_id": self.android_id,
                    "drm_id": self.drm_id,
                    "google_advertising_id": self.google_advertising_id,
                    "ip_address": self.ip_address,
                    "is_emulator": False,
                    "perf_id": self._generate_perf_id()
                },
                "name": "device_data_collection"
            },
            "meta": {
                "app": {
                    "app_variant": self.app_variant,
                    "build_type": "release",
                    "build_uuid": str(uuid.uuid4()),
                    "commit_hash": secrets.token_hex(20),
                    "id": self.client_id,
                    "type": "eats_app",
                    "version": self.version
                },
                "carrier": {
                    "mcc": "310",
                    "mnc": "260",
                    "name": "T-Mobile"
                },
                "device": {
                    "app_device_uuid": self.app_device_id,
                    "battery_level": round(random.uniform(0.5, 1.0), 1),
                    "battery_status": "unplugged",
                    "cpu_abi": ", arm64-v8a",
                    "device_id": self.device_id,
                    "drm_id": self.drm_id,
                    "google_advertising_id": self.google_advertising_id,
                    "google_play_services_status": "success",
                    "google_play_services_version": "25.47.30 (190400-833691957)",
                    "installation_id": self.installation_uuid,
                    "ip_address": self.ip_address,
                    "language": "en",
                    "locale": "en_US",
                    "manufacturer": "Google",
                    "model": self.model.lower(),
                    "os_arch": "aarch64",
                    "os_type": "android",
                    "os_version": self.os,
                    "os_version_build": "UE1A.230829.036.A4",
                    "screen_density": 3.2,
                    "screen_height_pixels": int(self.device_height),
                    "screen_width_pixels": int(self.device_width),
                    "thermal_state": "nominal",
                    "year_class": 2014
                },
                "network": {
                    "latency_band": "SLOW",
                    "type": "Unknown"
                },
                "session": {
                    "app_lifecycle_state": "foreground",
                    "cold_launch_id": self.cold_launch_id,
                    "foreground_start_time_ms": foreground_start_ms,
                    "hot_launch_id": self.hot_launch_id,
                    "session_id": self.client_session_uuid,
                    "session_start_time_ms": session_start_ms
                }
            }
        }
        
        return json.dumps(data)

    def build_device_data(self) -> str:
        BATTERY_STATUSES = ["charging", "discharging"]
        BATTERY_STATUSES = ['unplugged']
        epoch = self._generate_epoch()
        epoch_sci = f"{epoch:.12E}".replace("+", "")

        device_data = {
            "androidId": self.android_id,
            "batteryLevel": round(random.uniform(0.1, 1.0), 2),
            "batteryStatus": random.choice(BATTERY_STATUSES),
            "carrier": "",
            "carrierMcc": "",
            "carrierMnc": "",
            "course": 0.0,
            "cpuAbi": ", arm64-v8a, armeabi, armeabi-v7a",
            "deviceAltitude": 0.0,
            "deviceIds": {
                "androidId": self.android_id,
                "appDeviceId": self.app_device_id,
                "drmId": self.drm_id,
                "googleAdvertisingId": self.google_advertising_id,
                "googleAppSetId": self.google_app_set_id,
                "installationUuid": self.installation_uuid,
                "perfId": self._generate_perf_id(),
                "udid": self.udid,
                "unknownItems": {"a": []},
            },
            "deviceLatitude": float(self.latitude),
            "deviceLongitude": float(self.longitude),
            "deviceModel": self.model,
            "deviceOsName": "Android",
            "deviceOsVersion": self.os,
            "emulator": False,
            "epoch": {"value": "__EPOCH_PLACEHOLDER__"},
            "horizontalAccuracy": 0.0,
            "ipAddress": self.ip_address,
            "libCount": 0,
            "locationServiceEnabled": False,
            "mockGpsOn": False,
            "rooted": False,
            "sourceApp": "eats",
            "specVersion": "2.0",
            "speed": 0.0,
            "systemTimeZone": self.location_city,
            "unknownItems": {"a": []},
            "version": self.version,
            "versionChecksum": self.version_checksum,
            "verticalAccuracy": 0.0,
            "wifiConnected": True,
        }

        raw_json = json.dumps(device_data, separators=(",", ":"))
        raw_json = raw_json.replace('"__EPOCH_PLACEHOLDER__"', epoch_sci)
        raw_json = json.dumps(raw_json)
        return raw_json

    def build_usl_url(self) -> str:
        from urllib.parse import quote

        params = {
            "showDebugInfo": "false",
            "x-uber-device": "android",
            "x-uber-client-name": "eats",
            "x-uber-client-version": self.version,
            "x-uber-client-id": self.client_id,
            "firstPartyClientID": self.first_party_client_id,
            "isEmbedded": "true",
            "codeChallenge": self.pkce_challenge,
            "app_url": f"https://auth3.uber.com/applogin/{self.app_variant}",
            "asms": "true",
            "x-uber-device-udid": self.udid,
            "sim_mcc": "",
            "sim_mnc": "",
            "x-uber-app-device-id": self.app_device_id,
            "x-uber-device-location-latitude": self.latitude,
            "x-uber-device-location-longitude": self.longitude,
            "socialNative": "g",
            "x-uber-cold-launch-id": self.cold_launch_id,
            "x-uber-hot-launch-id": self.hot_launch_id,
            "x-uber-app-variant": self.app_variant,
            "countryCode": "",
            "known_user": "false",
            "isChromeCustomTabSession": "false",
        }

        items = []
        for k, v in params.items():
            if k == "app_url":
                items.append(f"{k}={quote(v, safe='')}")
            else:
                items.append(f"{k}={v}")

        return "https://auth.uber.com/v2?" + "&".join(items)

    def build_cit_token(self) -> str:
        # first /rt/devices/task request. not sure if this is relevant. doing this request possible for backend to initialize?
        # need to do more research. /rt/devices/results is the one that gives the cit token.

        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.drm_id,
            'x-uber-device': 'android',
            'x-uber-device-language': 'en_US',
            'user-agent': 'Cronet/129.0.6668.102@aa3a5623',
            'x-uber-device-os': self.os,
            'x-uber-device-sdk': self.sdk,
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-client-user-session-id': self.client_user_analytics_session_id,
            'x-uber-client-version': self.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.call_uuid,
            'x-uber-device-id': self.device_id,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.app_variant,
            'x-uber-analytics-session-id': self.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'uberctx-client-network-request-uuid': self.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self._generate_epoch())),
            'uberctx-cold-launch-id': self.cold_launch_id,
            'x-uber-client-id': self.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            'request': {
                'installationID': self.installation_uuid,
                'clientType': 'android',
                'clientIntegrityToken': '',
            },
        }
        json_data = json.dumps(json_data)

        response = requests.post('https://cn-geo1.uber.com/rt/devices/task', headers=headers, data=json_data)

        headers = {
            'x-uber-device-mobile-iso2': 'US',
            'x-uber-drm-id': self.drm_id,
            'x-uber-device': 'android',
            'x-uber-device-language': 'en_US',
            'user-agent': 'Cronet/129.0.6668.102@aa3a5623',
            'x-uber-device-os': self.os,
            'x-uber-device-sdk': self.sdk,
            'x-uber-request-uuid': str(uuid.uuid4()),
            'x-uber-client-user-session-id': self.client_user_analytics_session_id,
            'x-uber-client-version': self.version,
            'x-uber-device-manufacturer': 'Google',
            'x-uber-call-uuid': self.call_uuid,
            'x-uber-device-id': self.device_id,
            'x-uber-markup-textformat-version': '1',
            'x-uber-device-model': self.model,
            'uberctx-mobile-initiated': 'true',
            'x-uber-app-variant': self.app_variant,
            'x-uber-analytics-session-id': self.client_user_analytics_session_id,
            'content-type': 'application/json; charset=UTF-8',
            'x-uber-network-classifier': 'MEDIUM',
            'uberctx-client-network-request-uuid': self.client_network_request_uuid,
            'x-uber-device-epoch': str(int(self._generate_epoch())),
            'uberctx-cold-launch-id': self.cold_launch_id,
            'x-uber-client-id': self.client_id,
            'x-uber-app-lifecycle-state': 'foreground',
            'x-uber-protocol-version': '0.73.0',
            'x-uber-device-timezone': self.location_city,
            'x-uber-client-name': 'eats',
            'x-uber-client-session': self.client_session_uuid,
            'x-uber-device-time-24-format-enabled': '0',
            'x-uber-app-device-id': self.app_device_id,
            'x-uber-device-voiceover': '0',
            'priority': 'u=1, i',
        }

        json_data = {
            'request': {
                'installationID': self.installation_uuid,
                'keyAttestation': {
                    'certificate': '',
                },
                'attemptNumber': 1,
            },
        }
        json_data = json.dumps(json_data)

        response = requests.post('https://cn-geo1.uber.com/rt/devices/results', headers=headers, data=json_data)
        result = response.json()
        if result['status'] != 'UPSERT_STATUS_COMPLETE':
            print('Failed to generate CIT')
            print(response.json())
            print(response.status_code)
            return None

        print('Successfully got CIT Token')
        return result.get('clientIntegrityToken', None)
    
    def build_sig_token(self, headers: dict) -> str:
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

        sig_headers = {}
        for k, v in headers.items():
            k_lower = k.lower()
            if k_lower in ('x-uber-id', 'x-uber-cit'):
                continue
            if k_lower.startswith('x-uber-') or k_lower == 'authorization':
                sig_headers[k_lower] = v

        sorted_keys = sorted(sig_headers.keys())
        header_lines = "\n".join(f"{k}: {sig_headers[k]}" for k in sorted_keys)
        header_names = ";".join(sorted_keys)

        parts = ["a=ES256;v=1", 'POST', '/rt/silk-screen/submit-form', '']
        if header_lines:
            parts.append(header_lines)
        if header_names:
            parts.append(header_names)
        canonical = "\n".join(parts)

        signature = private_key.sign(canonical.encode('utf-8'), ec.ECDSA(hashes.SHA256()))

        return base64.b64encode(signature).decode()

    def generate_msm_attestation_token(self):
        header = {"alg": "ES256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode()).rstrip(b'=').decode()
        
        payload = {
            "requestDetails": {
                "requestPackageName": "com.ubercab.eats",
                "timestampMillis": str(int(time.time() * 1000)),
                "nonce": base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
            },
            "appIntegrity": {
                "appRecognitionVerdict": "PLAY_RECOGNIZED",
                "packageName": "com.ubercab.eats",
                "certificateSha256Digest": [base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()],
                "versionCode": "1"
            },
            "deviceIntegrity": {"deviceRecognitionVerdict": ["MEETS_DEVICE_INTEGRITY"]},
            "accountDetails": {"appLicensingVerdict": "LICENSED"}
        }
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).rstrip(b'=').decode()
        signature = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b'=').decode()
        
        return f"{header_b64}.{payload_b64}.{signature}"

    def get_device_fingerprint(self):
        spoof = Pixel9ProSpoof()
        return spoof.get_encoded_payload()

    def _generate_fingerprint_data(self):
        version = "131.0.6778.135"
        android_version = "15"

        now = datetime.now()
        unix_time = int(time.time() * 1000)

        audio_hash = hashlib.sha1(b"pixel9pro_audio_fingerprint").hexdigest()
        canvas_hash = hashlib.sha1(b"pixel9pro_canvas_fingerprint").hexdigest()
        canvas_detailed = hashlib.sha1(b"pixel9pro_canvas_fingerprint_detailed").hexdigest()
        emoji_hash = hashlib.sha256(b"pixel9pro_emoji").hexdigest()
        tag = self._generate_tag()
        cookie_tag = quote(tag, safe="")

        data = {
            "navigator.appVersion": f"5.0 (Linux; Android {android_version}; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36",
            "navigator.appName": "Netscape",
            "navigator.product": "Gecko",
            "navigator.platform": "Linux armv8l",
            "navigator.language": "en-US",
            "navigator.userAgent": f"Mozilla/5.0 (Linux; Android {android_version}; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36",
            "navigator.cookieEnabled": True,
            "navigator.hardwareConcurrency": 8,
            "navigator.deviceMemory": 8,
            "navigator.doNotTrack": "null",
            "navigator.automationEnabled": False,
            "navigator.maxTouchPoints": 5,
            "touchEnabled": True,
            "webdriver_detect": False,
            "navigator.vendor": "Google Inc.",
            "navigator.productSub": "20030107",
            "navigator.appCodeName": "Mozilla",
            "window.screen.colorDepth": "24",
            "window.screen.pixelDepth": "24",
            "window.screen.height": "2992",
            "window.screen.width": "1344",
            "window.screen.availHeight": "2847",
            "screen.availWidth": "1344",
            "screen.availHeight": "2847",
            "window.devicePixelRatio": "3",
            "window.screen.orientation.type": "portrait-primary",
            "window.screen.orientation.angle": "0",
            "window.screen.darkMode.enabled": False,
            "window.outerWidth": "448",
            "window.outerHeight": "949",
            "window.innerWidth": "448",
            "window.innerHeight": "865",
            "window.history.length": str(random.randint(1, 10)),
            "window.clientInformation.language": "en-US",
            "window.doNotTrack": "null",
            "navigator.userAgentData.brands": [
                {"brand": "Chromium", "version": "131"},
                {"brand": "Google Chrome", "version": "131"},
                {"brand": "Not_A Brand", "version": "24"}
            ],
            "navigator.userAgentData.mobile": True,
            "navigator.userAgentData.platform": "Android",
            "navigator.userAgentData.highEntropyValues.platform": "Android",
            "navigator.userAgentData.highEntropyValues.platformVersion": "15.0.0",
            "navigator.userAgentData.highEntropyValues.architecture": "arm",
            "navigator.userAgentData.highEntropyValues.bitness": "64",
            "navigator.userAgentData.highEntropyValues.model": "Pixel 9 Pro",
            "navigator.userAgentData.highEntropyValues.uaFullVersion": version,
            "navigator.userAgentData.highEntropyValues.fullVersionList": [
                {"brand": "Chromium", "version": version},
                {"brand": "Google Chrome", "version": version},
                {"brand": "Not_A Brand", "version": "24.0.0.0"}
            ],
            "webgl-supported": True,
            "webgl-version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
            "webgl-glsl-version": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
            "webgl-vendor": "WebKit",
            "webgl-renderer": "WebKit WebGL",
            "webgl-vendor-real": "ARM",
            "webgl-renderer-real": "Mali-G715-Immortalis MC11",
            "webgl-max-aa": "16",
            "webgl-unmasked-vendor": "ARM",
            "webgl-unmasked-renderer": "ANGLE (ARM, Mali-G715-Immortalis MC11, OpenGL ES 3.2)",
            "webgl-vertex-shader-highp-float": {"rangeMin": 127, "rangeMax": 127, "precision": 23},
            "webgl-vertex-shader-mediump-float": {"rangeMin": 15, "rangeMax": 15, "precision": 10},
            "webgl-fragment-shader-highp-float": {"rangeMin": 127, "rangeMax": 127, "precision": 23},
            "webgl-fragment-shader-mediump-float": {"rangeMin": 15, "rangeMax": 15, "precision": 10},
            "webgl-extensions": [
                "ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_color_buffer_half_float",
                "EXT_disjoint_timer_query", "EXT_float_blend", "EXT_frag_depth",
                "EXT_shader_texture_lod", "EXT_texture_filter_anisotropic", "EXT_sRGB",
                "KHR_parallel_shader_compile", "OES_element_index_uint", "OES_fbo_render_mipmap",
                "OES_standard_derivatives", "OES_texture_float", "OES_texture_float_linear",
                "OES_texture_half_float", "OES_texture_half_float_linear", "OES_vertex_array_object",
                "WEBGL_color_buffer_float", "WEBGL_compressed_texture_astc", "WEBGL_compressed_texture_etc",
                "WEBGL_compressed_texture_etc1", "WEBGL_debug_renderer_info", "WEBGL_debug_shaders",
                "WEBGL_depth_texture", "WEBGL_draw_buffers", "WEBGL_lose_context", "WEBGL_multi_draw",
                "WEBGL_provoking_vertex"
            ],
            "webgl2-supported": True,
            "webgl2-version": "WebGL 2.0 (OpenGL ES 3.0 Chromium)",
            "webgl2-glsl-version": "WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)",
            "ac-base-latency": 0.005333333333333333,
            "ac-output-latency": 0,
            "ac-sample-rate": 48000,
            "ac-state": "running",
            "ac-max-channel-count": 2,
            "ac-number-of-inputs": 1,
            "ac-number-of-outputs": 1,
            "ac-channel-count": 2,
            "ac-channel-count-mode": "explicit",
            "ac-channel-interpretation": "speakers",
            "ac-fft-size": 2048,
            "ac-frequency-bin-count": 1024,
            "ac-min-decibels": -100,
            "ac-max-decibels": -30,
            "ac-smoothing-time-constant": 0.8,
            "ac-print": audio_hash,
            "ac-print-raw": "124.04344884395687",
            "canvas-print-100-999": canvas_hash,
            "canvas-print-detailed-100-999": canvas_detailed,
            "canvas_spoofing": 0,
            "time-unix-epoch-ms": unix_time,
            "time-local": now.strftime("%m/%d/%Y, %I:%M:%S %p"),
            "time-string": now.strftime("%a %b %d %Y %H:%M:%S GMT-0800 (Pacific Standard Time)"),
            "time-tz-offset-minutes": -480,
            "time-tz-has-dst": "true",
            "time-tz-dst-active": "false",
            "time-tz-std-offset": -480,
            "time-tz-fixed-locale-string": "3/6/2014, 7:58:39 AM",
            "navigator.connection.effectiveType": "4g",
            "navigator.connection.rtt": 50,
            "navigator.connection.saveData": False,
            "navigator.battery.level": str(round(random.uniform(0.5, 1.0), 2)),
            "navigator.battery.charging": str(random.choice([True, False])).lower(),
            "navigator.battery.chargingTime": "Infinity",
            "navigator.battery.dischargingTime": str(random.randint(10000, 50000)),
            "browser-features": {
                "css_reflections_support": False,
                "css_scrollbar_support": True,
                "custom_protocol_handler_support": True,
                "effective_type": True,
                "filesystem_support": True,
                "font_display_support": True,
                "input_search_event_support": True,
                "input_types_month_support": True,
                "input_types_week_support": True,
                "prefetch_support": True,
                "quota_management_support": True,
                "speech_recognition_support": True,
                "todataurl_webp_support": True,
                "vibrate_support": True,
                "video_hls": False,
                "web_sql_database_support": True,
                "hairline": True,
            },
            "ex_browser_type": "Chrome Webkit",
            "css-flags": {
                "pointer-type": "coarse",
                "screen-interface": "touch",
                "color-scheme": "light",
                "reduced-motion": False,
                "display-flex": True,
                "display-grid": True,
            },
            "_t": CCJS_TOKEN,
            "cookie-_cc": cookie_tag,
            "cookie-_cid_cc": cookie_tag,
            "dom-local-tag": tag,
            "cid-dom-local-tag": tag,
            "dom-session-tag": tag,
            "cid-dom-session-tag": tag,
            "fresh-cookie": "true",
            "cf_flags": "1022963",
            "ccjs_version": "IIHGun4MNYWxXjVZRxge8w==",
            "private-browser": {"browser": "Chrome", "enabled": False},
            "navigator.storage.persisted": False,
            "document.storage.access": False,
            "granted-permissions": {
                "accelerometer": "granted",
                "gyroscope": "granted",
                "magnetometer": "granted",
                "geolocation": "prompt",
                "camera": "prompt",
                "microphone": "prompt",
                "notifications": "prompt",
            },
            "mobile-device-motion": {
                "acceleration": {"x": "0.000", "y": "0.000", "z": "0.000"},
                "acceleration.including.gravity": {"x": "0.000", "y": "9.800", "z": "0.000"},
                "rotation": {"alpha": "0.000", "beta": "0.000", "gamma": "0.000"},
            },
            "mobile-device-orientation": {
                "absolute": False,
                "alpha": 0,
                "beta": 0,
                "gamma": 0,
            },
            "webgl_noise_detect": 0,
            "emjh": emoji_hash,
            "flash-installed": "false",
            "flash-enabled": "false",
            "media-capabilities": {
                "video-decode-h264": {"supported": True, "smooth": True, "powerEfficient": True},
                "video-decode-h265": {"supported": True, "smooth": True, "powerEfficient": True},
                "video-decode-vp8": {"supported": True, "smooth": True, "powerEfficient": True},
                "video-decode-vp9": {"supported": True, "smooth": True, "powerEfficient": True},
                "video-decode-av1": {"supported": True, "smooth": True, "powerEfficient": True},
                "audio-decode-aac": {"supported": True, "smooth": True, "powerEfficient": True},
                "audio-decode-opus": {"supported": True, "smooth": True, "powerEfficient": True},
            },
            "timing-sync-collection": random.randint(45, 85),
            "timing-total-collection": random.randint(180, 320),
            "script-load-time": int(time.time() * 1000) - random.randint(500, 2000),
            "device-data-captured-time": int(time.time() * 1000),
            "performance-now-precision": 0.1,
            "date-now-offset": random.randint(-2, 2),
            "drm-widevine-supported": True,
            "drm-widevine-level": "L1",
            "hdr-support": True,
            "hdr10-plus": True,
            "dolby-vision": False,
        }

        return data

    def _generate_tag(self):
        return CCJS_TAG

    def _encode_payload(self, data):
        json_str = json.dumps(data, separators=(",", ":"))
        return xor_base64_utf8(json_str)
