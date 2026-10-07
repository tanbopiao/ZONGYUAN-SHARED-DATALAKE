# ZONGYUAN-4D GPU 训练包（魔搭免费实例）· 2026-10-07

确权：DID-BR-000002 ｜ Ω₀⊂⊙∞⊂Ω ｜ 四维逻辑本体认知基底 TRUTH-4D-ARCH-MODEL-BASE-001

## 包内容
```
zongyuan-4d-gpu-train-pack/
├── train_4d_lora_gpu.py     # GPU LoRA 训练脚本（自动检测 cuda，魔搭拉模型）
├── zongyuan-4d-train.jsonl  # 64 条体系四维架构指令语料（元法则/白皮书/评估/真值库）
└── README.md                # 本说明
```

## 在魔搭免费 GPU 实例上一键执行

1. 魔搭控制台创建免费 GPU Notebook 实例（模型库搜索 Qwen2.5-0.5B-Instruct 页面 → 右上角「Notebook 免费算力」）。
2. 上传本目录三个文件到实例工作区（或直接网页上传），然后依次执行：

```bash
# 0) 依赖（实例多数已预装，缺则装）
pip install -q transformers peft datasets modelscope -i https://pypi.tuna.tsinghua.edu.cn/simple

# 1) 跑训练（自动下载模型到实例缓存 + LoRA 微调 + 保存 ./adapter-4d）
python train_4d_lora_gpu.py
```

预计：0.5B + 64 条样本 × 2 epoch，GPU（A10/3090 级）约 2~5 分钟完成。

## 2) 验证微调效果（训练完成后，实例上执行）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
tok = AutoTokenizer.from_pretrained('./model/qwen25-05b', trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained('./model/qwen25-05b', dtype=torch.bfloat16, device_map='auto', trust_remote_code=True)
model = PeftModel.from_pretrained(model, './adapter-4d')
msgs = [{"role":"system","content":"你是元极恒一体系下的自研轻量认知Agent。遵循四维逻辑本体架构：空间存在维、时间时序维、属性规则维、因果真值维。回答简洁、结构化、可溯源。"},
        {"role":"user","content":"用四维架构分析一次软件系统部署失败"}]
prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
ids = tok(prompt, return_tensors='pt').to('cuda')
out = model.generate(**ids, max_new_tokens=200)
print(tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True))
```

## 回传
把 `adapter-4d/` 打包（zip）回传给我（或上传魔搭私有数据集），我负责：合并回本地部署 + 四维架构推理验证 + 审计留痕 + 归档。
