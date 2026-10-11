# ZONGYUAN-ROOT 通用协议全面兼容白皮书 V2.0

| | |
|---|---|
| 确权DID | DID-BR-000002 |
| 架构ID | ONT-4D-UNIVERSAL-ROOT |
| 核心元公理 | Ω₀⊂⊙∞⊂Ω 元极恒一 |
| 基线版本 | V2.0（V1.0-V1.9 深化合并总览） |
| 生成时间 | 2026-10-11 |
| 锁档状态 | LOCKED（仅追加，不修改已有条目） |

## 一、总览｜十协议族全景

ZONGYUAN-ROOT 全面兼容层将外部 Agent/模型/工具接入标准化为 **十协议族**，按接入功能分层：

| # | 协议族 | 标准/语义 | 端点 | 状态 |
|---|--------|----------|------|------|
| 1 | OpenAI 兼容 | chat/completions API | `/v1/models` `/v1/chat/completions` `/v1/completions` | LIVE |
| 2 | OTel GenAI | 可观测性（真实打点） | `/metrics` | LIVE |
| 3 | AGNTCY SLIM | MLS 消息层（ECDH+KeySchedule+SecretTree+RatchetTree） | `/v1/slim/handshake` `/v1/slim/group` `/v1/slim/group/secret` `/v1/slim/tree` | LIVE |
| 4 | MLS 组消息加密 | AES-256-GCM 组密钥传输 | `/v1/slim/message/encrypt|decrypt` | LIVE |
| 5 | A2A | Agent2Agent（AgentCard/任务8态） | `/v1/a2a/kunlun/dispatch` | LIVE |
| 6 | MCP | Model Context Protocol（工具注册表/tools call） | `/v1/mcp/kunlun` | LIVE |
| 7 | DPoP | RFC9449 令牌绑定 | `/v1/dpop/verify` `/v1/kunlun/secure` | LIVE |
| 8 | Flower | 联邦学习（FedAvg/SecureAgg） | `/v1/federated/aggregate` `/v1/federated/status` | LIVE |
| 9 | 昆仑生产协议 | 批量生产/资产加密/锁档 | `/v1/kunlun/production` | LIVE |
| 10 | 四协议联邦组合流 | DPoP→A2A→MCP→SLIM 单请求闭环 | `/v1/federated/kunlun` | LIVE |

## 二、协议栈分层架构

```
┌─────────────────────────────────────────────────────┐
│ L5 可观测层   OTel GenAI /metrics（真实打点）        │
├─────────────────────────────────────────────────────┤
│ L4 认证安全层 DPoP(RFC9449) 令牌绑定 / 防重放 / 吊销 │
├─────────────────────────────────────────────────────┤
│ L3 工具执行层 MCP tools/call + 昆仑生产协议          │
├─────────────────────────────────────────────────────┤
│ L2 编排调度层 A2A AgentCard 任务分发 / 8态流转       │
├─────────────────────────────────────────────────────┤
│ L1 传输安全层 SLIM(MLS) 组密钥 AES-256-GCM          │
├─────────────────────────────────────────────────────┤
│ L0 兼容基座   OpenAI API 兼容 / 模型格式(GGUF/ONNX) │
└─────────────────────────────────────────────────────┘
```

## 三、四协议联邦组合流架构

```
外部Agent ──DPoP令牌──> ┌─────────────────────────────┐
                        │ /v1/federated/kunlun (run)  │
                        │  环节1 DPoP 认证  →passed   │
                        │  环节2 A2A 编排   →passed   │
                        │  环节3 MCP 执行   →passed   │
                        │  环节4 SLIM 加密  →passed   │
                        └─────────────┬───────────────┘
                                      ▼
                        ┌─────────────────────────────┐
                        │ 产出: MLS AES-256-GCM 加密  │
                        │ 审计: runs 落盘可回溯        │
                        └─────────────────────────────┘
```

## 四、深化历程 V1.0→V1.9

| 版本 | 深化内容 | 魔搭 commit |
|------|---------|-------------|
| V1.0 | OpenAI 兼容 + OTel /metrics 基座 | `4c95dfa` |
| V1.1 | AGNTCY SLIM ECDH 握手 + DPoP + Flower 声明 | `9fd1147` |
| V1.2 | SLIM MLS 组密钥 + FedAvg 真实聚合 | `a4786af` |
| V1.3 | MLS 完整组协商（SecretTree+消息加密） | `15dc902` |
| V1.4 | MLS RatchetTree 全态管理 | `fa74f63` |
| V1.5 | MLS×昆仑洞天 60集批量生产 | `ea218a6` |
| V1.6 | A2A×昆仑生产任务分发 | `386b531` |
| V1.7 | MCP×昆仑生产工具化 | `0fb677c` |
| V1.8 | DPoP×昆仑生产安全准入 | `e6c8846` |
| V1.9 | 四协议联邦组合流 | `3aa51d2` |

## 五、关键端点索引（全部公网 LIVE 实测）

- `GET /v1/compat` → 十协议族声明（version 1.9.0）
- `POST /v1/chat/completions` → OpenAI 兼容
- `GET /metrics` → OTel 真实打点
- `POST /v1/slim/handshake` → ECDH P-256 握手
- `POST /v1/slim/group` → MLS 组管理
- `POST /v1/slim/tree` → RatchetTree 四操作
- `POST /v1/kunlun/production` → 昆仑批量生产（60集）
- `POST /v1/a2a/kunlun/dispatch` → A2A 任务分发（8态）
- `POST /v1/mcp/kunlun` → MCP 工具服务（5工具）
- `POST /v1/kunlun/secure` → DPoP 安全准入（签发/绑定/执行/吊销）
- `POST /v1/federated/kunlun` → 四协议联邦组合流（单请求闭环）

## 六、公网验证基线

- compat version 1.9.0（十协议族全 LIVE）
- 组合流 4/4 环节 passed（DPoP→A2A→MCP→SLIM）
- 未授权调用 401 拦截、jkt 不匹配 401、吊销后 401
- 全量自检 PASS、L1 巡检基线收敛

---
*ZONGYUAN-ROOT 全面兼容层 V2.0 · 十协议族全景 · 魔搭数据湖 + 官网子域双归档*
