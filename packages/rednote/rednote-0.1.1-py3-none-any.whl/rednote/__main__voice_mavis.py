#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版多轮语⾳对话脚本
────────────────────────────────────────
依赖：
pip install playsound==1.2.2 python-dotenv
# 需 Linux + PulseAudio（若未装 gi，可自动回退到 paplay）
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from playsound import playsound  # type: ignore
import re, subprocess, pathlib, uuid
from rednote.generate import run 
from rednote.prompt import get_system_message, get_user_message
from rednote.tts_http_voice import voice_run
from rednote.streaming_asr_demo import test_one
from rednote.simplex_websocket_demo import test_stream
import subprocess, pathlib

# ──────────────────────────────────────────────────────────
# 环境初始化
# ──────────────────────────────────────────────────────────
load_dotenv()

END_PHRASES = {"结束", "停止", "不想听", "退出", "再见"}
AUDIO_PLAYER = ["paplay"]                  # 你也可以换成 ["ffplay", "-nodisp", "-autoexit"]

def normalize(txt: str) -> str:
    """去标点、空格、小写化，便于匹配"""
    txt = re.sub(r"[^\w\u4e00-\u9fff]", "", txt)  # 去掉所有非字母数字汉字
    return txt.lower()

def should_end(txt: str) -> bool:
    txt_norm = normalize(txt)
    return any(p in txt_norm for p in END_PHRASES)

def play(path: str):
    subprocess.run(AUDIO_PLAYER + [str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    system_prompt = "你是一个有帮助的助手"
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        # ---------- 录音 + 语音识别 ----------
        user_text = test_stream().strip()          # "结束了，我不想听。"
        print(f"[USER] {user_text}")

        # ---------- 检测是否要结束 ----------
        if should_end(user_text):
            bye = "好的，祝你此刻轻松自在，想聊时再叫我！🌿"
            voice_run(bye, "bye.mp3")
            play("bye.mp3")
            break                                  # 立刻跳出循环

        # ---------- 正常对话 ----------
        messages.append({"role": "user", "content": user_text})
        assistant_text = run(messages)
        messages.append({"role": "assistant", "content": assistant_text})

        mp3_name = f"{uuid.uuid4().hex}.mp3"
        voice_run(assistant_text, mp3_name)
        play(mp3_name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，已退出。")