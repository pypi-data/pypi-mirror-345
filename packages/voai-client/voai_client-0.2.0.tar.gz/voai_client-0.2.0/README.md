# voai‑client — Python SDK & CLI for **voai.ai VoiceAPI**

`voai‑client` 旨在讓您用最簡單的方式存取 **voai.ai** 的雲端文字轉語音服務，完整封裝以下 API：

| 功能 | VoiceAPI 方法 | HTTP 端點 |
|------|---------------|-----------|
| 取得 Speaker 列表 | `get_speakers()` | `GET /TTS/GetSpeaker` |
| 短文本 TTS | `speech()` | `POST /TTS/Speech` |
| 長文本 TTS | `generate_voice()` | `POST /TTS/generate-voice` |
| 多角色對話 TTS | `generate_dialogue()` | `POST /TTS/generate-dialogue` |
| 查詢金鑰用量 | `get_usage()` | `GET /Key/Usage` |

---
## 安裝


### 從程式庫安裝
```
pip install -e .
```

### 從 pypi 安裝
```bash
pip install voai-client
```

---
## 快速上手
### 建立 `VoiceAPI` 實例
```python
from voai_client import VoiceAPI
api = VoiceAPI("YOUR_API_KEY")  # x-api-key 會自動附加到所有請求
```

### 1️⃣ 取得 Speaker 列表
```python
speakers = api.get_speakers()
print(speakers[0])  # ➜ {"name": "佑希", "language": "zh-TW", ...}
```

### 2️⃣ 短文本 TTS
```python
wav = api.speech(
    text="網際智慧的聲音，是業界的標竿。",
    speaker="佑希",
    version="Neo",
    style="預設",
)
api.save_audio(wav, "short.wav")
```

### 3️⃣ 長文本 TTS（支援 `[:秒]` 停頓標籤）
```python
long_text = (
    "網際智慧的聲音，不僅清晰自然，還融入了情感與真實感，"
    "展現了[:2]先進技術的極致魅力。它是業界的標竿。"
)
wav = api.generate_voice(long_text, name="佑希")
api.save_audio(wav, "long.wav")
```

### 4️⃣ 多角色對話 TTS
```python
dialogue = [
    {"voai_script_text": "今天的進度會議[:1.5]你準備好了嗎？", "preset_id": "neo_佑希"},
    {"voai_script_text": "差不多了，我剛把簡報做完。", "preset_id": "default_子墨"},
]

presets = [
    {"id": "neo_佑希", "voice": {"name": "佑希", "style": "聊天", "version": "Neo"}},
    {"id": "default_子墨", "voice": {"name": "子墨", "style": "預設", "version": "Classic"}},
]

wav = api.generate_dialogue(dialogue, preset_speakers=presets)
api.save_audio(wav, "dialogue.wav")
```

### 5️⃣ 查詢 API 用量
```python
usage = api.get_usage()
print(usage)  # ➜ {'quota': 100000, 'remaining': 98234, ...}
```

---
## CLI 用法
安裝後會自帶 `voai-cli`，所有子指令皆需 `--api-key`：

```bash
# 列出所有 speaker
voai-cli --api-key $VOAI_KEY speakers

# 短文本 TTS
voai-cli --api-key $VOAI_KEY speech "你好世界" 佑希 --outfile hello.wav

# 長文本 TTS（讀取文字檔）
voai-cli --api-key $VOAI_KEY generate article.txt 佑希 --outfile article.wav

# 多角色對話 TTS（讀取 JSON）
voai-cli --api-key $VOAI_KEY dialogue dialogue.json --outfile talk.wav

# 查詢金鑰用量
voai-cli --api-key $VOAI_KEY usage
```

`dialogue.json` 範例：
```json
{
  "input": {
    "preset_speakers": [
      {"id": "neo_佑希", "voice": {"name": "佑希", "style": "聊天", "version": "Neo"}},
      {"id": "default_子墨", "voice": {"name": "子墨", "style": "預設", "version": "Classic"}}
    ],
    "dialogue": [
      {"voai_script_text": "今天的進度會議[:1.5]你準備好了嗎？", "preset_id": "neo_佑希"},
      {"voai_script_text": "差不多了，我剛把簡報做完。", "preset_id": "default_子墨"}
    ]
  }
}
```

---
## 參數對照表
| 參數 | 說明 | 範圍 / 預設 |
|-------|------|-------------|
| `speed` | 語速 | `0.5 – 1.5`，預設 `1` |
| `pitch_shift` | 音調 | `‑5 – 5`，預設 `0` |
| `style_weight` | 風格權重（僅 Classic 有效）| `0 – 1`，預設 `0` |
| `breath_pause` | 句間停頓（秒）| `0 – 10`，預設 `0` |

> **停頓標籤**：`[:秒]` 支援小數點後一位，最大 `5` 秒；任兩標籤間建議至少 20 字以保持自然度。
