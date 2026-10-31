# direct_api_digg.py
import time
import uuid
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor

# Direct mobile API endpoint for liking (digging) an aweme_id using pooled sessionids
API_URL = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/commit/item/digg/"

def calc_gorgon_stub(params: str, cookie: str) -> dict:
    ts = int(time.time())
    rticket = int(time.time() * 1000)
    sig_seed = f"{params}{cookie}{ts}".encode()
    x_gorgon = "0404b0d30000" + hashlib.md5(sig_seed).hexdigest()[:40]
    return {
        "X-Gorgon": x_gorgon,
        "X-Khronos": str(ts),
        "_rticket": str(rticket)
    }

def send_like(aweme_id: str, session_id: str, proxy: str = None):
    device_id = str(uuid.uuid4().int)[:19]
    iid = str(uuid.uuid4().int)[:19]
    params = (
        f"aweme_id={aweme_id}&type=1&channel_id=0"
        f"&device_id={device_id}&iid={iid}&aid=1233"
        f"&app_name=musical_ly&version_code=340104"
        f"&device_platform=android&os_version=13"
    )
    cookie_str = f"sessionid={session_id}"
    sig = calc_gorgon_stub(params, cookie_str)

    headers = {
        "User-Agent": "com.zhiliaoapp.musically/2023401040 (Linux; U; Android 13; en_US; Pixel 7; Build/TQ3A.230805.001; Cronet/TTNetVersion:6c7b701a)",
        "Cookie": cookie_str,
        "X-Gorgon": sig["X-Gorgon"],
        "X-Khronos": sig["X-Khronos"]
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    r = requests.get(f"{API_URL}?{params}&_rticket={sig['_rticket']}", headers=headers, proxies=proxies, timeout=10)
    return r.status_code, r.text[:120]

if __name__ == "__main__":
    AWEME_ID = "7123456789012345678"
    SESSIONS = ["paste_sessionid_1", "paste_sessionid_2"]
    with ThreadPoolExecutor(max_workers=10) as ex:
        for sid in SESSIONS:
            fut = ex.submit(send_like, AWEME_ID, sid)
            print(fut.result())
