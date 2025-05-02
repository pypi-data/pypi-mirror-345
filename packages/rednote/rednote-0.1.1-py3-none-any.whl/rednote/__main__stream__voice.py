# from dotenv import load_dotenv
# from rednote.generate import run
# from rednote.prompt import get_system_message,get_user_message
# from rednote.tts_http_voice import voice_run,base64,json,uuid,requests
# from rednote.streaming_asr_demo import test_one
# from rednote.test import test_stream
# from rednote.simplex_websocket_demo import record



# load_dotenv()

# def main():
#     system_prompt="你是一个有帮助的助手"
#     messages=[{
#             "role":"system","content":system_prompt}]
    
#     count=0
#     while True:
        
        
#         count+=1
#         first_stream=test_stream("src/rednote/stream.wav")
#         second_stream=run(messages)
#         print(f"""first:{first_stream}""")
#         messages.append({"role":"user","content":first_stream})
#         messages.append({"role":"assistant","content":second_stream})
#         print(f"""message: {messages}""")
#         if count>=3:
#             break
        
# if __name__=="__main__":
#     main()
    