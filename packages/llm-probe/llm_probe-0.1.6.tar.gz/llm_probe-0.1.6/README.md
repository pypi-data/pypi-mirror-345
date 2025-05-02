<!---
Copyright 2024 The HyperAccel. All rights reserved.
-->

<p align="center">
    <br>
    <img src="docs/images/logo.png" width="400"/>
    <br>
<p>

# LLM Probe: Tool for extracting intermediate data from HuggingFace LLM models using PyTorch Hooks

LLM Probe는 HuggingFace LLM 모델의 중간 데이터를 PyTorch Hook을 이용해 추출하는 도구입니다.

## Installation Requirements
- Python 3.10 이상
- PyTorch 2.4.0 이상
- HuggingFace Transformers 4.35.0 이상

## Installation Method

### Install from PyPI
LLM Probe 프레임워크는 pip을 통해 설치할 수 있습니다:
```bash
pip install llm-probe
```

### Build from Source
LLM Probe 프레임워크는 소스 코드에서 설치할 수 있습니다:
```bash
# Clone the repository
git clone https://github.com/Hyper-Accel/llm-probe.git
cd llm-probe

# Install the package with Makefile script
make install INSTALL_MODE=[dev|release] PYTHON_VERSION=[3.10|3.11|3.12]
source .venv/bin/activate
```

설치 옵션:

- INSTALL_MODE: 설치 모드 지정 (기본값: dev)
    - dev: 개발용 패키지 설치 (ruff, pytest, pre-commit 등) 및 편집 가능 모드로 설치
    - release: 프로덕션용 패키지만 설치
- PYTHON_VERSION: Python 버전 지정 (기본값: 3.10)

## Usage

LLM-Probe를 사용하려면, Python 코드에서 해당 모듈을 임포트하고 hook을 적용할 모듈 이름을 지정하면 됩니다. 그 후 모델 추론을 수행하면 PyTorch hook이 자동으로 작동하며 원하는 중간 데이터를 추출할 수 있습니다. 아래는 사용 예시입니다:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# LLM probe 패키지 임포트
from llm_probe.probe import HFModelProbe
from llm_probe.logger import get_logger

# 로거 초기화
logger = get_logger("HuggingFace probe 예제 코드")
logger.setLevel("DEBUG")

# 모델과 토크나이저 다운로드
model = AutoModelForCausalLM.from_pretrained("gpt2-medium")
tokenizer = AutoTokenizer.from_pretrained("gpt2-medium")

# 모델 probe 생성
model_probe = HFModelProbe(model, tokenizer)

# "transformer.h.0.ln_1" 모듈에 hook 설정
module = "transformer.h.0.ln_1"
model_probe.set_hook(module)

# 추론 수행
input_ids = model_probe.get_input_ids("Hello")
model_probe.generate(input_ids, max_new_tokens=1)

# 중간 데이터 가져오기
ln_1_input = model_probe.get_intermediate_input(module, dtype=torch.float16)
ln_1_output = model_probe.get_intermediate_output(module, dtype=torch.float16)
ln_1_weight = model_probe.get_intermediate_weight(module, dtype=torch.float16)
ln_1_bias = model_probe.get_intermediate_bias(module, dtype=torch.float16)
```
