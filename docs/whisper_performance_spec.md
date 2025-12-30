# Whisper 效能優化規格書

## 概述

本專案使用 Whisper 進行語音識別，目標是提供高品質的字幕轉錄。本文檔記錄效能優化方案。

---

## 當前配置

```json
{
  "whisper": {
    "model": "medium",
    "language": "en",
    "task": "transcribe",
    "temperature": 0,
    "word_timestamps": true
  }
}
```

### 模型選擇指南

| 模型 | VRAM | 速度 | 準確度 | 適用場景 |
|------|------|------|--------|---------|
| tiny | ~1 GB | 最快 | 低 | 快速預覽 |
| base | ~1.5 GB | 快 | 中 | 短片、簡單內容 |
| small | ~2.5 GB | 中 | 高 | 一般使用 |
| **medium** | ~5 GB | 慢 | **更高** | **長片翻譯（推薦）** |
| large-v3 | ~10 GB | 最慢 | 最高 | 專業品質需求 |

---

## 效能優化方案

### 方案一：faster-whisper（推薦升級）

使用 CTranslate2 引擎，相比 openai-whisper：
- **4x 更快**的推論速度
- **50% 更少**的記憶體使用
- 支援 INT8 量化

#### 安裝

```bash
pip uninstall openai-whisper
pip install faster-whisper
```

#### 使用方式

```python
from faster_whisper import WhisperModel

model = WhisperModel("medium", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    video_path,
    language="en",
    word_timestamps=True,
    vad_filter=True  # 跳過靜音段落
)

for segment in segments:
    print(f"[{segment.start:.2f}s] {segment.text}")
```

#### compute_type 選項

| 類型 | 設備 | 速度 | VRAM |
|------|------|------|------|
| `float16` | GPU | 快 | 中 |
| `int8_float16` | GPU | 更快 | 低 |
| `int8` | CPU | 最快 | 最低 |

---

### 方案二：GPU 加速

#### 確認 CUDA 可用

```python
import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

#### 安裝 CUDA 版 PyTorch

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

---

## 效能預估

### 單一影片處理時間

| 影片長度 | CPU | GPU | faster-whisper GPU |
|---------|-----|-----|-------------------|
| 1 分鐘 | ~60s | ~15s | ~5s |
| 5 分鐘 | ~5min | ~75s | ~20s |
| 10 分鐘 | ~10min | ~2.5min | ~40s |

---

## 快速檢測腳本

```python
# check_whisper_setup.py
import torch

print("=== Whisper 環境檢測 ===")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

try:
    import whisper
    print(f"openai-whisper: OK")
except ImportError:
    print("openai-whisper: Not installed")

try:
    from faster_whisper import WhisperModel
    print(f"faster-whisper: OK")
except ImportError:
    print("faster-whisper: Not installed")
```

---

## 升級計畫

- [ ] 安裝 faster-whisper
- [ ] 更新 translate_video.py 支援 faster-whisper
- [ ] 效能測試比較
- [ ] 確認穩定後切換預設引擎

---

*更新日期: 2025-12-31*
