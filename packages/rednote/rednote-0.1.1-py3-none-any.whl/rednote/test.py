import asyncio
import datetime
import gzip
import json
import time
import uuid
import wave
from io import BytesIO

import aiofiles
import websockets


# ────────────────────────── 协议常量 ──────────────────────────
PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

FULL_CLIENT_REQUEST   = 0b0001
AUDIO_ONLY_REQUEST    = 0b0010
FULL_SERVER_RESPONSE  = 0b1001
SERVER_ACK            = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

NO_SEQUENCE       = 0b0000
POS_SEQUENCE      = 0b0001
NEG_SEQUENCE      = 0b0010
NEG_WITH_SEQUENCE = 0b0011

NO_SERIALIZATION = 0b0000
JSON             = 0b0001

NO_COMPRESSION = 0b0000
GZIP            = 0b0001


# ────────────────────────── 工具函数 ──────────────────────────
def generate_header(message_type=FULL_CLIENT_REQUEST,
                    message_type_specific_flags=NO_SEQUENCE,
                    serial_method=JSON,
                    compression_type=GZIP,
                    reserved_data=0x00):
    header = bytearray()
    header_size = 1
    header.append((PROTOCOL_VERSION << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    return header


def generate_before_payload(sequence: int):
    return sequence.to_bytes(4, "big", signed=True)


def parse_response(res: bytes) -> dict:
    protocol_version = res[0] >> 4
    header_size      = res[0] & 0x0F
    message_type     = res[1] >> 4
    message_flags    = res[1] & 0x0F
    serialization    = res[2] >> 4
    compression      = res[2] & 0x0F

    payload = res[header_size * 4:]
    rst = {
        "message_type": message_type,
        "flags": message_flags,
        "is_last_package": bool(message_flags & 0x02),
    }

    if message_flags & 0x01:                          # 有 sequence
        rst["payload_sequence"] = int.from_bytes(payload[:4], "big", signed=True)
        payload = payload[4:]

    if message_type == FULL_SERVER_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg  = payload[4:]
    elif message_type == SERVER_ACK:
        return rst                                    # ACK 直接返回
    elif message_type == SERVER_ERROR_RESPONSE:
        rst["code"] = int.from_bytes(payload[:4], "big")
        payload_size = int.from_bytes(payload[4:8], "big")
        payload_msg  = payload[8:]
    else:
        return rst

    if compression == GZIP:
        payload_msg = gzip.decompress(payload_msg)
    if serialization == JSON:
        payload_msg = json.loads(payload_msg.decode())
    else:
        payload_msg = payload_msg.decode(errors="ignore")

    rst["payload_msg"]  = payload_msg
    rst["payload_size"] = payload_size
    return rst


def read_wav_info(data: bytes):
    with BytesIO(data) as f:
        wf = wave.open(f, "rb")
        nch, sw, fr, nf = wf.getparams()[:4]
        return nch, sw, fr, nf, wf.readframes(nf)


# ────────────────────────── WS Client ──────────────────────────
class AsrWsClient:
    def __init__(self, audio_path, **kwargs):
        self.audio_path = audio_path

        self.seg_duration = int(kwargs.get("seg_duration", 100))
        self.ws_url       = kwargs.get("ws_url",
                        "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel")

        self.uid     = kwargs.get("uid", "test")
        self.format  = kwargs.get("format", "wav")
        self.rate    = kwargs.get("rate", 16000)
        self.bits    = kwargs.get("bits", 16)
        self.channel = kwargs.get("channel", 1)
        self.codec   = kwargs.get("codec", "raw")

        self.streaming    = kwargs.get("streaming", True)
        self.mp3_seg_size = kwargs.get("mp3_seg_size", 1000)

        self.access_key = kwargs.get("access_key", "YOUR_ACCESS_KEY")
        self.app_key    = kwargs.get("app_key",    "YOUR_APP_KEY")

    # ---------- 构造首包 ----------
    def construct_request(self, reqid):
        return {
            "user": {"uid": self.uid},
            "audio": {
                "format": self.format,
                "sample_rate": self.rate,
                "bits": self.bits,
                "channel": self.channel,
                "codec": self.codec,
            },
            "request": {"model_name": "bigmodel", "enable_punc": True},
        }

    @staticmethod
    def slice_data(data, chunk):
        for off in range(0, len(data), chunk):
            end  = min(off + chunk, len(data))
            yield data[off:end], end == len(data)

    # ---------- 主流程 ----------
    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        reqid = str(uuid.uuid4())
        seq   = 1

        payload = gzip.compress(json.dumps(self.construct_request(reqid)).encode())
        first   = bytearray(generate_header(message_type_specific_flags=POS_SEQUENCE))
        first.extend(generate_before_payload(seq))
        first.extend(len(payload).to_bytes(4, "big"))
        first.extend(payload)

        headers = {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Access-Key":  "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_",
            "X-Api-App-Key":      "1787492884",
            "X-Api-Request-Id":  reqid,
        }

        printed_text = ""
        seen_seq     = set()

        async with websockets.connect(self.ws_url,
                                    additional_headers=headers,
                                    max_size=1_000_000_000) as ws:
            await ws.send(first)
            await ws.recv()                    # 扔掉握手 ACK

            for chunk, last in self.slice_data(wav_data, segment_size):
                seq += 1
                flag = NEG_WITH_SEQUENCE if last else POS_SEQUENCE

                body = gzip.compress(chunk)
                msg  = bytearray(generate_header(message_type=AUDIO_ONLY_REQUEST,
                                                message_type_specific_flags=flag))
                msg.extend(generate_before_payload(-seq if last else seq))
                msg.extend(len(body).to_bytes(4, "big"))
                msg.extend(body)
                await ws.send(msg)

                # --------------- 处理响应 ---------------
                res = parse_response(await ws.recv())

                # >>> 变动开始 ─── 只打印“新增的文字”
                if res["message_type"] != FULL_SERVER_RESPONSE:
                    continue

                seq_no = res.get("payload_sequence")
                if seq_no in seen_seq:
                    continue
                seen_seq.add(seq_no)

                text = res.get("payload_msg", {}) \
                        .get("result", {}) \
                        .get("text", "")

                if text and text != printed_text:
                    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"[{ts}] {text}")
                    printed_text = text
                # <<< 变动结束 ────────────────────────────

                if res["is_last_package"]:
                    break

                if self.streaming:
                    await asyncio.sleep(self.seg_duration / 1000)

        return printed_text

    async def execute(self):
        async with aiofiles.open(self.audio_path, "rb") as f:
            raw = await f.read()

        if self.format == "wav":
            nch, sw, fr, nf, _pcm = read_wav_info(raw)
            seg = int(nch * sw * fr * self.seg_duration / 1000)
            return await self.segment_data_processor(raw, seg)

        if self.format == "pcm":
            seg = int(self.rate * 2 * self.channel * self.seg_duration / 1000)
            return await self.segment_data_processor(raw, seg)

        if self.format == "mp3":
            return await self.segment_data_processor(raw, self.mp3_seg_size)

        raise ValueError("Unsupported audio format")


# ────────────────────────── 简易包装 ──────────────────────────
def execute_one(audio_path: str, **kwargs):
    return asyncio.run(AsrWsClient(audio_path, **kwargs).execute())


def test_stream(wav_file: str):
    print("▶ 流式测试开始")
    text = execute_one(wav_file)
    print("▶ 最终转写:", text)
    return text


# ────────────────────────── CLI ──────────────────────────
# if __name__ == "__main__":
#     test_stream("src/rednote/stream.wav")   # ← 换成你的音频路径
