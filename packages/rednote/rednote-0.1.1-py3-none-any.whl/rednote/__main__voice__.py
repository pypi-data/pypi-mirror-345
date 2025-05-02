# from dotenv import load_dotenv
# from rednote.generate import run
# from rednote.prompt import get_system_message,get_user_message
# from rednote.tts_http_voice import voice_run,base64,json,uuid,requests
# from rednote.streaming_asr_demo import test_one


# load_dotenv()

# def main():
#     system_prompt="你是一个有帮助的助手"
#     messages=[{
#             "role":"system","content":system_prompt}]
    
#     count=0
#     while True:
#         count+=1
#         first_run=run(messages)
#         mp3_name=f"""{count}.mp3"""
#         voice_run(first_run,mp3_name)
#         # 多轮对话
#         result=test_one("voice.mp3")
#         print(f"Raw result from test_one: {json.dumps(result, indent=2, ensure_ascii=False)}")
#         text=extract_text(result)
#         if text and text.strip():
#                 messages.append({"role":"assistant","content":first_run})
#                 messages.append({"role":"user","content":text})
#         else:
#             print("error value")
#         if count>=5:
#                     break
        

# def extract_text(res: dict) -> str | None:
#     """
#     从 test_one 的返回结构里取到用户说的话。
#     会选置信度最高的一条；如果都没有 text 或都为空，则返回 None
#     """
#     try:
#         items = res["result"]["payload_msg"]["result"]
#         if not isinstance(items, list):
#             return None

#         # 选置信度最高的那条
#         best = max(
#             (item for item in items if isinstance(item, dict) and "text" in item),
#             key=lambda x: x.get("confidence", 0),
#             default=None
#         )
#         if best:
#             txt = best.get("text", "").strip()
#             return txt if txt else None
#     except (KeyError, TypeError):
#         pass
#     return None

# if __name__=="__main__":
#     main()