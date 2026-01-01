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

## CPU 模式優化

當系統沒有可用的 GPU 或 CUDA 環境時，Whisper 會自動回退到 CPU 模式運行。以下說明如何優化 CPU 模式下的效能表現。

### CPU 多線程設定

faster-whisper 提供兩個重要的 CPU 多線程參數：

| 參數 | 說明 | 預設值 | 建議設定 |
|------|------|--------|---------|
| `cpu_threads` | 單一推論任務使用的線程數 | 4 | CPU 核心數的 50-75% |
| `num_workers` | 並行處理的工作者數量 | 1 | 1-2（避免記憶體過載） |

#### 使用方式

```python
from faster_whisper import WhisperModel

# 根據 CPU 核心數設定線程
import os
cpu_count = os.cpu_count() or 4

model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8",           # CPU 建議使用 int8 量化
    cpu_threads=max(1, cpu_count // 2),  # 使用一半的核心數
    num_workers=1                   # 單一工作者避免記憶體競爭
)
```

#### 參數調優建議

- **cpu_threads**：設定過高可能導致線程競爭，反而降低效能。建議從核心數的 50% 開始測試。
- **num_workers**：多工作者會增加記憶體使用量，在記憶體有限的環境建議保持為 1。
- **compute_type**：CPU 模式下務必使用 `int8` 量化，可大幅減少運算量與記憶體使用。

### CPU 降級模型策略

當 GPU 不可用時，建議自動降級使用較小的模型以維持可接受的處理速度：

| 原始設定 | 降級模型 | 原因 |
|---------|---------|------|
| large-v3 | medium | large 模型在 CPU 上過慢 |
| medium | small | 平衡速度與準確度 |
| small | small | 維持原設定 |
| base/tiny | 維持原設定 | 已是輕量模型 |

#### 自動降級實作範例

```python
import torch
from faster_whisper import WhisperModel

def get_optimal_model(preferred_model: str = "medium") -> tuple[str, str, str]:
    """
    根據硬體環境自動選擇最佳模型配置

    Returns:
        tuple: (model_name, device, compute_type)
    """
    if torch.cuda.is_available():
        # GPU 可用，使用偏好設定
        return preferred_model, "cuda", "float16"

    # CPU 模式：降級模型
    cpu_model_map = {
        "large-v3": "medium",
        "large": "medium",
        "medium": "small",
    }

    actual_model = cpu_model_map.get(preferred_model, preferred_model)

    if actual_model != preferred_model:
        print(f"[警告] GPU 不可用，模型從 {preferred_model} 降級為 {actual_model}")

    return actual_model, "cpu", "int8"

# 使用範例
model_name, device, compute_type = get_optimal_model("medium")
model = WhisperModel(model_name, device=device, compute_type=compute_type)
```

### CPU 多線程效能預估

以下為不同線程數配置下的預估加速比（基準：單線程處理 10 分鐘影片）：

| CPU 線程數 | 相對加速比 | 預估處理時間 | 備註 |
|-----------|-----------|-------------|------|
| 1 | 1.0x | ~25 分鐘 | 基準線 |
| 2 | 1.7x | ~15 分鐘 | 明顯提升 |
| 4 | 2.8x | ~9 分鐘 | **建議值（4核心CPU）** |
| 8 | 4.0x | ~6 分鐘 | 適合 8 核心以上 CPU |
| 16 | 5.5x | ~4.5 分鐘 | 高階 CPU，收益遞減 |

> **注意事項**：
> - 以上數據為使用 `small` 模型搭配 `int8` 量化的預估值
> - 實際效能受 CPU 型號、記憶體頻寬、系統負載等因素影響
> - 超過物理核心數的線程設定通常不會帶來額外加速

### CPU 模式完整配置範例

```python
import os
import torch
from faster_whisper import WhisperModel

def create_cpu_optimized_model():
    """建立針對 CPU 優化的 Whisper 模型"""

    cpu_count = os.cpu_count() or 4
    optimal_threads = max(1, int(cpu_count * 0.75))

    print(f"[CPU 模式] 偵測到 {cpu_count} 核心，使用 {optimal_threads} 線程")

    model = WhisperModel(
        "small",                    # CPU 建議使用 small 模型
        device="cpu",
        compute_type="int8",        # 強制使用 int8 量化
        cpu_threads=optimal_threads,
        num_workers=1
    )

    return model

def transcribe_with_cpu_optimization(model, audio_path):
    """使用 CPU 優化參數進行轉錄"""

    segments, info = model.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
        vad_filter=True,            # 跳過靜音加速處理
        condition_on_previous_text=False
    )

    return list(segments), info
```

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

- [x] 安裝 faster-whisper
- [x] 更新 translate_video.py 支援 faster-whisper
- [ ] 效能測試比較
- [ ] 確認穩定後切換預設引擎

---

## VAD 過濾效益

### 什麼是 VAD（Voice Activity Detection）

VAD（語音活動偵測）是一種技術，用於自動識別音訊中的語音段落與靜音段落。在 faster-whisper 中，可透過 `vad_filter=True` 參數啟用此功能。

### 主要優點

1. **跳過靜音段落**：VAD 會自動偵測並跳過沒有語音的片段，避免對靜音區域進行不必要的轉錄處理。

2. **處理速度提升**：預估可提升 10-30% 的處理速度，具體提升幅度取決於影片中靜音段落的比例。

3. **減少無意義的空白字幕**：避免產生只有標點符號或空白的無效字幕段落，提升最終字幕品質。

### 使用方式

```python
segments, info = model.transcribe(
    audio_path,
    vad_filter=True,           # 啟用 VAD 過濾
    vad_parameters={
        "min_silence_duration_ms": 500  # 可選：調整靜音判定閾值
    }
)
```

---

## condition_on_previous_text 參數說明

### 參數功能

`condition_on_previous_text` 參數控制是否將前一段轉錄結果作為下一段的上下文條件。

### 設定建議

| 設定值 | 效果 | 適用場景 |
|--------|------|---------|
| `True` | 改善連貫性，語句銜接更自然 | 對話連貫性要求高的內容 |
| `False`（建議預設）| 避免錯誤傳播 | 一般使用、品質優先 |

### 注意事項

- **設為 True 的優點**：可改善前後語句的連貫性，特別是在長句被切分時能保持語意完整。

- **設為 True 的風險**：可能導致錯誤傳播（hallucination），即前一段的轉錄錯誤會影響後續段落，產生重複或虛構的內容。

- **建議預設為 False**：除非明確需要高連貫性，否則建議保持 False 以確保每段轉錄獨立，避免錯誤累積。

### 使用方式

```python
segments, info = model.transcribe(
    audio_path,
    condition_on_previous_text=False  # 建議預設值
)
```

---

*更新日期: 2026-01-01*
