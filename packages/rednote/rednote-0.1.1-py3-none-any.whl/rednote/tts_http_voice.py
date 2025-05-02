

'''
requires Python 3.6 or later
pip install requests
'''
import base64
import json
import uuid
import requests

# 填写平台申请的appid, access_token以及cluster
def voice_run(messages, filename):
    print(f"messages:{messages},filename:{filename}")
    appid = "1787492884"
    access_token= "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_"
    cluster = "volcano_tts"

    voice_type = "BV001_streaming"
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"

    header = {"Authorization": f"Bearer;{access_token}"}

    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088"
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": messages,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }

    try:
            resp = requests.post(api_url, json.dumps(request_json), headers=header)
            if "data" in resp.json():
                data = resp.json()["data"]
                file_to_save = open(filename, "wb")
                file_to_save.write(base64.b64decode(data))
    except Exception as e:
            e.with_traceback()
