import random as rnd
import hashlib as hsh
import time as tme
import base64 as b64
import json as jsn
from datetime import datetime as dtt
from urllib.parse import quote

CCJS_TOKEN = "AU3DAsLmFWtIgqtMtbLbS4w+32SSNYk0AQS9WYyPUuOLhqEUCPK47i3ypCM9lWN66r3bI8CKv6g0/nR1HGPLSmIJz9rr9OvT+yYvqYutAAsCNPB37oDtWKScPMbZkKMekyaAhhoRP7gY4cOXmQp5TLTx600WoD0Ym9qhqZqZ2DgpdECred+9GXB9UX4BJbT0YabTYmtTX5NAHOVB+Gh4gdoeG//nire/I36pWIVWDvrJivw9Apah5BGR/tkoBh8zL9dLXaCKGg2/haK6oADbhHiJGjh0Sw3potxmf3vh/+tjGK9UNSkJqNqgRVdqgxrUP254aleIH7v+TvDcarsjlrSGehsQbJjYYeJT1+bW3YL3PzeLuckP0hNqztGMzmA="
CCJS_TAG = CCJS_TOKEN[:24]
XOR_KEY = [89, 231, 225, 55]

def xor_base64_utf8(payload: str) -> str:
    xored = "".join(chr(ord(ch) ^ XOR_KEY[i % len(XOR_KEY)]) for i, ch in enumerate(payload))
    return b64.b64encode(xored.encode("utf-8")).decode("ascii")

class Pixel9ProSpoof:

    width = 1344
    hei = 2992
    dpr = 3
    cdp = 24
    pde = 24
    awi = 1344
    ahe = 2847
    inw = 448
    inh = 865
    outw = 448
    outh = 949

    def __init__(slf):
        slf.dd = {}
        slf.gen()

    def gen(slf):
        slf.nav()
        slf.scr()
        slf.win()
        slf.ua()
        slf.wgl()
        slf.auc()
        slf.can()
        slf.tim()
        slf.con()
        slf.bat()
        slf.bfe()
        slf.css()
        slf.stg()
        slf.misc()

    def nav(slf):
        ver = "131.0.6778.135"
        av = "15"
        slf.dd.update({
            "navigator.appVersion": f"5.0 (Linux; Android {av}; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Mobile Safari/537.36",
            "navigator.appName": "Netscape",
            "navigator.product": "Gecko",
            "navigator.platform": "Linux armv8l",
            "navigator.language": "en-US",
            "navigator.userAgent": f"Mozilla/5.0 (Linux; Android {av}; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Mobile Safari/537.36",
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
        })

    def scr(slf):
        slf.dd.update({
            "window.screen.colorDepth": str(slf.cdp),
            "window.screen.pixelDepth": str(slf.pde),
            "window.screen.height": str(slf.hei),
            "window.screen.width": str(slf.width),
            "window.screen.availHeight": str(slf.ahe),
            "screen.availWidth": str(slf.awi),
            "screen.availHeight": str(slf.ahe),
            "window.devicePixelRatio": str(slf.dpr),
            "window.screen.orientation.type": "portrait-primary",
            "window.screen.orientation.angle": "0",
            "window.screen.darkMode.enabled": False,
        })

    def win(slf):
        slf.dd.update({
            "window.outerWidth": str(slf.outw),
            "window.outerHeight": str(slf.outh),
            "window.innerWidth": str(slf.inw),
            "window.innerHeight": str(slf.inh),
            "window.history.length": str(rnd.randint(1, 10)),
            "window.clientInformation.language": "en-US",
            "window.doNotTrack": "null",
        })

    def ua(slf):
        ver = "131.0.6778.135"
        slf.dd.update({
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
            "navigator.userAgentData.highEntropyValues.uaFullVersion": ver,
            "navigator.userAgentData.highEntropyValues.fullVersionList": [
                {"brand": "Chromium", "version": ver},
                {"brand": "Google Chrome", "version": ver},
                {"brand": "Not_A Brand", "version": "24.0.0.0"}
            ],
        })

    def wgl(slf):
        slf.dd.update({
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
                "ANGLE_instanced_arrays",
                "EXT_blend_minmax",
                "EXT_color_buffer_half_float",
                "EXT_disjoint_timer_query",
                "EXT_float_blend",
                "EXT_frag_depth",
                "EXT_shader_texture_lod",
                "EXT_texture_filter_anisotropic",
                "EXT_sRGB",
                "KHR_parallel_shader_compile",
                "OES_element_index_uint",
                "OES_fbo_render_mipmap",
                "OES_standard_derivatives",
                "OES_texture_float",
                "OES_texture_float_linear",
                "OES_texture_half_float",
                "OES_texture_half_float_linear",
                "OES_vertex_array_object",
                "WEBGL_color_buffer_float",
                "WEBGL_compressed_texture_astc",
                "WEBGL_compressed_texture_etc",
                "WEBGL_compressed_texture_etc1",
                "WEBGL_debug_renderer_info",
                "WEBGL_debug_shaders",
                "WEBGL_depth_texture",
                "WEBGL_draw_buffers",
                "WEBGL_lose_context",
                "WEBGL_multi_draw",
                "WEBGL_provoking_vertex",
            ],
            "webgl2-supported": True,
            "webgl2-version": "WebGL 2.0 (OpenGL ES 3.0 Chromium)",
            "webgl2-glsl-version": "WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)",
        })

    def auc(slf):
        ah = hsh.sha1(b"pixel9pro_audio_fingerprint").hexdigest()
        slf.dd.update({
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
            "ac-print": ah,
            "ac-print-raw": "124.04344884395687",
        })

    def can(slf):
        cb = b"pixel9pro_canvas_fingerprint"
        ch = hsh.sha1(cb).hexdigest()
        cdh = hsh.sha1(cb + b"_detailed").hexdigest()
        slf.dd.update({
            "canvas-print-100-999": ch,
            "canvas-print-detailed-100-999": cdh,
            "canvas_spoofing": 0,
        })

    def tim(slf):
        nw = dtt.now()
        uts = int(tme.time() * 1000)
        toff = -480
        slf.dd.update({
            "time-unix-epoch-ms": uts,
            "time-local": nw.strftime("%m/%d/%Y, %I:%M:%S %p"),
            "time-string": nw.strftime("%a %b %d %Y %H:%M:%S GMT-0800 (Pacific Standard Time)"),
            "time-tz-offset-minutes": toff,
            "time-tz-has-dst": "true",
            "time-tz-dst-active": "false",
            "time-tz-std-offset": toff,
            "time-tz-fixed-locale-string": "3/6/2014, 7:58:39 AM",
        })

    def con(slf):
        slf.dd.update({
            "navigator.connection.effectiveType": "4g",
            "navigator.connection.rtt": 50,
            "navigator.connection.saveData": False,
        })

    def bat(slf):
        slf.dd.update({
            "navigator.battery.level": str(rnd.uniform(0.5, 1.0)),
            "navigator.battery.charging": str(rnd.choice([True, False])).lower(),
            "navigator.battery.chargingTime": "Infinity",
            "navigator.battery.dischargingTime": str(rnd.randint(10000, 50000)),
        })

    def bfe(slf):
        slf.dd.update({
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
        })

    def css(slf):
        slf.dd.update({
            "css-flags": {
                "pointer-type": "coarse",
                "screen-interface": "touch",
                "color-scheme": "light",
                "reduced-motion": False,
                "display-flex": True,
                "display-grid": True,
            },
        })

    def stg(slf):
        tg = slf.tg()
        cookie_tag = quote(tg, safe="")
        slf.dd.update({
            "_t": CCJS_TOKEN,
            "cookie-_cc": cookie_tag,
            "cookie-_cid_cc": cookie_tag,
            "dom-local-tag": tg,
            "cid-dom-local-tag": tg,
            "dom-session-tag": tg,
            "cid-dom-session-tag": tg,
            "fresh-cookie": "true",
            "cf_flags": "1022963",
            "ccjs_version": "IIHGun4MNYWxXjVZRxge8w==",
        })

    def misc(slf):
        slf.dd.update({
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
            "emjh": hsh.sha256(b"pixel9pro_emoji").hexdigest(),
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
            "timing-sync-collection": rnd.randint(45, 85),
            "timing-total-collection": rnd.randint(180, 320),
            "script-load-time": int(tme.time() * 1000) - rnd.randint(500, 2000),
            "device-data-captured-time": int(tme.time() * 1000),
            "performance-now-precision": 0.1,
            "date-now-offset": rnd.randint(-2, 2),
            "drm-widevine-supported": True,
            "drm-widevine-level": "L1",
            "hdr-support": True,
            "hdr10-plus": True,
            "dolby-vision": False,
        })

    def tg(slf) -> str:
        return CCJS_TAG

    def get_device_data(slf) -> dict:
        return slf.dd.copy()

    def get_encoded_payload(slf) -> str:
        st = jsn.dumps(slf.dd, separators=(",", ":"))
        return xor_base64_utf8(st)

    def get_headers(slf) -> dict:
        ver = "131.0.6778.135"
        return {
            "User-Agent": f"Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Mobile Safari/537.36",
            "Sec-Ch-Ua": '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Ch-Ua-Platform-Version": '"15.0.0"',
            "Sec-Ch-Ua-Model": '"Pixel 9 Pro"',
            "Sec-Ch-Ua-Full-Version": ver,
            "Sec-Ch-Ua-Arch": '"arm"',
            "Sec-Ch-Ua-Bitness": '"64"',
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def update_timestamps(slf):
        slf.tim()
        slf.bat()

def create_pixel9pro_fingerprint() -> dict:
    px = Pixel9ProSpoof()
    return px.get_device_data()

def get_pixel9pro_headers() -> dict:
    px = Pixel9ProSpoof()
    return px.get_headers()