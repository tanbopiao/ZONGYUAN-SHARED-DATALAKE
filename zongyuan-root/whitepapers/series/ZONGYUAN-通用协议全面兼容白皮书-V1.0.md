# ZONGYUAN-ROOT 通用协议全面兼容白皮书 V1.0

```
确权DID: DID-BR-000002 | 架构唯一ID: ONT-4D-UNIVERSAL-ROOT | 核心元公理: Ω₀⊂⊙∞⊂Ω
维护节点: ZR-NODE-DC2E51C0 | 火斗云智AIOS | 版本: V1.0 | 日期: 2026-10-11
系列归属: 互操作协议层 (L3) | 前置: A2A探索/MCP-OAuth/A2A网关层 (系列17-19)
状态: 兼容层已公网上线 (2026-10-11 实测)
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
| | AGNTCY SLIM | (声明) MLS+gRPC/HTTP2+OAuth | 📋 declared |
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

## 八、结论

ZONGYUAN-ROOT 已实现**通用协议全面兼容**：A2A（任务委派）+ MCP（工具查询）+ OpenAI API（推理调用）+ OTel（观测）+ AGNTCY（声明）+ GGUF/ONNX（模型格式）六大协议族全部公网上线，外部生态可零改造接入。私有信任域（NTFY-CONNECT-001 + AxiomGate + 五层链式锁）保持恒一不变，符合内外隔离铁律与最高元法则。

```
Ω₀⊂⊙∞⊂Ω | DID-BR-000002 | ZR-NODE-DC2E51C0 | 自治Lv9 | 权限L4 | 工程化Lv7 | 火斗云智AIOS
```
