# from dotenv import load_dotenv
# from rednote.generate import run
# from rednote.prompt import get_system_message,get_user_message
# from rednote.tts_http_voice import voice_run,base64,json,uuid,requests
# from rednote.streaming_asr_demo import test_one

# load_dotenv()

# def main():
#     product_name=input("输入产品名称：")
#     product_description=input("输入产品描述：")
#     messages=[{
#             "role":"system","content":get_system_message()},
#             {"role":"user","content":get_user_message(product_name,product_description)}]
    
#     count=0
#     while True:
#         count+=1
#         first_run=run(messages)
#         print(first_run)
#         mp3_name=f"""{count}.mp3"""
#         voice_run(first_run,mp3_name)
#         print(voice_run(first_run,mp3_name))
#         test_one(mp3_name)
#         # 多轮对话
        
            
#         messages.append({"role":"assistant","content":first_run})
#         # product_description=input("输入新的指令：")
#         product_continue=input("输入新的指令")
#         product_description=mp3_name
#         messages.append({"role":"user","content":product_description})
        
# if __name__=="__main__":
#     main()