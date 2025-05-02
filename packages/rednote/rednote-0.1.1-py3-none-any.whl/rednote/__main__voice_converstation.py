from dotenv import load_dotenv
from rednote.generate import run
from rednote.prompt import get_system_message,get_user_message
from rednote.tts_http_voice import voice_run,base64,json,uuid,requests
from rednote.streaming_asr_demo import test_one
from rednote.test import test_stream
from rednote.simplex_websocket_demo import record,test_stream                   # 新增
import uuid  
import subprocess, pathlib




load_dotenv()

def main():
    system_prompt="你是一个有帮助的助手"
    messages=[{
            "role":"system","content":system_prompt}]
    
    count=0
    USER_TEXT={"结束","退出","拜拜","再见","break out","bye"}
    while True:
        count+=1
        first_stream=test_stream()
        second_stream=run(messages)
        
        
        messages.append({"role":"user","content":first_stream})
        messages.append({"role":"assistant","content":second_stream})
        print(f"""message: {messages}""")
        
        # 播放生成的内容
        mp3_name=f"""{count}.mp3"""
        voice_run(second_stream,mp3_name)
        
        
        subprocess.run(["paplay", pathlib.Path(mp3_name)])
        if count>=2:
            break
        
if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户终止，退出")
    