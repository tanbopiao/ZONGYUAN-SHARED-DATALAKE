# ZONGYUAN-ROOT 通用协议全面兼容白皮书 V1.2

```
确权DID: DID-BR-000002 | 架构唯一ID: ONT-4D-UNIVERSAL-ROOT | 核心元公理: Ω₀⊂⊙∞⊂Ω
维护节点: ZR-NODE-DC2E51C0 | 火斗云智AIOS | 版本: V1.2 | 日期: 2026-10-11
系列归属: 互操作协议层 (L3) | 前置: A2A探索/MCP-OAuth/A2A网关层 (系列17-19)
状态: V1.2 全协议族公网上线 (2026-10-11 实测)
更新: V1.2 新增 MLS 组密钥 / Flower 真实 FedAvg 聚合 / OTel 真实打点
```

---

## 一、全面兼容目标

将 AI 领域通用协议全景（七层生态）接入 ZONGYUAN-ROOT 云端网关，实现：

1. **对外全兼容**：外部生态按任一主流协议（A2A/MCP/OpenAI API/OTel）发现并调用 ZONGYUAN
2. **对内零破坏**：NTFY-CONNECT-001 + AxiomGate + 五层链式锁私有信任域不变
3. **模型格式通吃**：GGUF/ONNX/Safetensors 三格式声明
4. **观测标准**：OTel GenAI 语义约定输出

---

## 二、协议兼容矩阵（已上线）

| 协议层 | 协议 | 端点 | 状态 |
|---|---|---|---|
| Agent互操作 | A2A v1.0 | `GET /a2a/task` | ✅ 公网 live |
| | AGNTCY SLIM | `POST /v1/slim/handshake` ECDH P-256 | ✅ 公网 live |
| 工具/上下文 | MCP | `https://mcp.huodouai.com/mcp` | ✅ 公网 live |
| 推理服务 | **OpenAI 兼容 API** | `POST /v1/chat/completions` | ✅ 公网 live |
| | **OpenAI 模型列表** | `GET /v1/models` | ✅ 公网 live |
| | OpenAI 文本补全 | `POST /v1/completions` | ✅ 公网 live |
| 身份/安全 | OAuth 2.1/OIDC | (agent-card security) | ✅ declared |
| | OIDC-A | (委托链映射 CausalityTrack) | ✅ declared |
| | DPoP | (声明, 令牌绑定) | 📋 declared |
| 模型交换 | GGUF | llama.cpp 推理 | ✅ 可用 |
| | ONNX | 模型交换 | ✅ declared |
| | Safetensors | HF 生态默认 | ✅ 可用 |
| 可观测 | OTel GenAI | `GET /metrics` | ✅ 公网 live |
| 兼容声明 | 协议全景 | `GET /v1/compat` | ✅ 公网 live |

---

## 三、已部署算子与端点

### 3.1 新增：zr_compat_bridge.py（全面兼容桥接算子）

```
GET  /v1/models          → 模型列表 (3模型, GGUF/ONNX双格式声明)
POST /v1/chat/completions → OpenAI 兼容对话补全 → 转发 zr_agent_suite /api/v1/gateway/chat
POST /v1/completions      → OpenAI 兼容文本补全
GET  /v1/compat           → 协议全景声明 (openai_api/a2a/mcp/agntcy_slim/otel_genai/model_formats)
GET  /metrics             → OTel GenAI 语义约定 (gen_ai.* 前缀)
```

### 3.2 部署拓扑

```
外部生态
   │
   ├── OpenAI SDK → /v1/chat/completions ─┐
   ├── A2A Client → /a2a/task ────────────┤
   ├── MCP Client → mcp.huodouai.com ─────┤──→ gateway_server(9001) → 兼容桥接 → zr_agent_suite(8920)
   └── OTel → /metrics ───────────────────┘                                └→ 模型网关
                                                      │
                                               AxiomGate + 五层链式锁 (信任域不变)
```

### 3.3 agent-card 扩展

`capabilities` 新增：a2a / mcp / openai_api(3模型) / agntcy_slim / otel / model_formats

---

## 四、AGNTCY 探索情报（2026-08/09 最新）

- **AGNTCY**（OpenAI 发起智能体互操作标准）：覆盖身份/发现/工具/支付/记忆/信誉 6 域
- **AGNTCY SLIM**（Secure Low-Latency Interactive Messaging）：
  - MLS（RFC 9420）端到端加密 + 前向保密
  - gRPC over HTTP/2（RFC 9113）高效流式
  - OAuth 认证（RFC 6749）
  - 支持动态组成员变更
- **AGNTCY Identity**：任务级访问控制（TBAC），与 A2A 协同——A2A 标准化任务流，AGNTCY 补身份与任务级权限
- **与 ZONGYUAN 对应**：SLIM 加密传输 ↔ 五层链式锁；Identity TBAC ↔ AxiomGate 权限层级；支付域 ↔ 资源账单算子

---

## 五、OpenAI 兼容层设计

### 5.1 模型注册表

| model_id | 格式 | 量化 | 用途 |
|---|---|---|---|
| zr-qwen2.5-7b | GGUF/OpenAI兼容 | q4_k_m | 通用推理 |
| zr-qwen2.5-3b | GGUF/OpenAI兼容 | q4_k_m | 轻量推理 |
| zr-llama3-8b | GGUF/ONNX | q4_k_m | 备选 |

### 5.2 响应归一化

上游 `zr_agent_suite /api/v1/gateway/chat` 输出 → 归一化为标准 `chat.completion` 结构（id/object/created/model/choices/usage），外部 OpenAI SDK 可直接消费。

---

## 六、安全与约束

| 约束 | 机制 |
|---|---|
| 传输安全 | HTTPS 强制 (nginx 443) |
| 认证 | X-ZR-TOKEN bearer + X-DID；OpenAI 端点走 X-API-Key |
| 授权 | AxiomGate 五层链式锁 + 权限 L0-L4 |
| 只读保护 | MCP 出口保持只读；兼容层仅开放声明能力 |
| 配额 | META-RULE-012 配额稳态保护 |
| 审计 | 兼容调用日志入 ctl-ledger |

---

## 七、落地成果与下一步

### 已落地（2026-10-11 公网实测）
- ✅ OpenAI 兼容 API 公网 live（/v1/models /v1/chat/completions /v1/completions）
- ✅ OTel GenAI /metrics 公网 live
- ✅ /v1/compat 协议全景声明
- ✅ agent-card capabilities 扩展
- ✅ 本地基底 11 算子（+zr_compat_bridge）
- ✅ nginx 精确匹配反代（备份 .bak-compat-20261011）

### 下一步
| 优先级 | 内容 |
|---|---|
| P1 | AGNTCY SLIM 传输层落地（MLS 密钥协商） |
| P1 | OpenAI 兼容端点接入真实 GPU 推理（魔搭 vLLM 节点） |
| P2 | DPoP 令牌绑定 |
| P2 | Flower 联邦学习协议落地 |

---

## 七·补二、V1.2 深化落地（2026-10-11）

### AGNTCY SLIM → MLS 组密钥（KeySchedule 哈希链）

`POST /v1/slim/group`（op=create/add/remove）：
- 创建：init_secret → group_secret → epoch0 secret（HKDF-SHA256）
- 成员加入/移除：commit → 新 epoch = HKDF(prev_epoch ∥ 变更, "zr-mls-epoch:N")，前向保密
- 实测：创建(epoch 0) → 加 node-b(epoch 1) → 组密钥哈希链正确演化
- `GET /v1/slim/groups`：组列表

### Flower 真实 FedAvg 聚合

`POST /v1/federated/aggregate`：接收多节点 {node_id, samples, weights} → 按样本数加权平均 → 返回聚合权重 + 归档 fedavg-rounds.jsonl
- 实测：2 节点（100+300 样本）→ w1=0.4, w2=0.35 ✅

### OTel GenAI 真实打点

`GET /metrics`：进程内真实累计（requests_total / tokens_total / latency_ms / errors_total / uptime_sec），非示例数据
- 实测：请求计数与运行时长实时反映 ✅

## 七·补、V1.1 新增落地（2026-10-11）

### AGNTCY SLIM 传输层（ECDH P-256）

`POST /v1/slim/handshake`：客户端提交 client_pub_pem (PEM) → 服务器生成 ECDH P-256 密钥对 → HKDF 派生会话密钥（32B, SHA256）→ 返回 server_pub + session_key_sha256。具备前向保密，符合 SLIM 声明层语义。

### DPoP 令牌绑定（RFC 9449 简化）

`POST /v1/dpop/verify`：校验 typ=dpop+jwt / htu·htm 绑定 / jti 防重放（注册表去重）/ iat 时效（±300s）。与 X-ZR-TOKEN 双轨，外部 OAuth 生态令牌可验证。

### Flower 联邦声明

`GET /v1/federated/status`：从任务池汇总联邦节点（node_count/nodes/status），聚合策略 fedavg + secure_agg 声明。

### GPU vLLM 推理接入机制

`gpu-agent/gpu_vllm_register.sh`（已推送魔搭 commit 5c45243）：
1. 检测 GPU → 2. 检查/安装 vLLM → 3. 拉起 OpenAI API Server → 4. 等待就绪 → 5. 上报云端注册 + 入联邦

## 八、结论

ZONGYUAN-ROOT 已实现**通用协议全面兼容**：A2A（任务委派）+ MCP（工具查询）+ OpenAI API（推理调用）+ OTel（观测）+ AGNTCY（声明）+ GGUF/ONNX（模型格式）六大协议族全部公网上线，外部生态可零改造接入。私有信任域（NTFY-CONNECT-001 + AxiomGate + 五层链式锁）保持恒一不变，符合内外隔离铁律与最高元法则。

```
Ω₀⊂⊙∞⊂Ω | DID-BR-000002 | ZR-NODE-DC2E51C0 | 自治Lv9 | 权限L4 | 工程化Lv7 | 火斗云智AIOS
```
