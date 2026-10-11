# Ω₀⊂⊙∞⊂Ω ZONGYUAN-ROOT 通用协议全面兼容 · 十二协议族全景（V2.2）

> **生产级多智能体联邦自治操作系统**——一套协议层，把 Agent / 模型 / 工具 / GPU 全部标准化接入。不拼参数，拼系统架构。
>
> 确权 DID：`DID-BR-000002` ｜ 架构 ID：`ONT-4D-UNIVERSAL-ROOT` ｜ 基线：LOCKED（仅追加，不修改）

---

## 一、为什么值得看

| 数字 | 含义 |
|---|---|
| **12** | 十二协议族全 LIVE（OpenAI 兼容 → OTel → SLIM/MLS → A2A → MCP → DPoP → Flower → OAuth2/OIDC → SSE/WebSocket …） |
| **4/4** | 四协议联邦组合流单请求闭环（DPoP→A2A→MCP→SLIM）全部环节通过 |
| **12 代** | 深化版本链 V1.0→V2.2，每代公网实测 |
| **LIVE** | 全部关键端点公网可访问、可验证 |
| **1.5B** | 本地小模型 + 强编排，低成本跑通生产级自治流水线 |

## 二、十二协议族全景（V2.2）

| # | 协议族 | 标准/语义 | 端点 | 状态 |
|---|---|---|---|---|
| 1 | OpenAI 兼容 | chat/completions API（vLLM/Ollama 真实 GPU 路由） | `/v1/chat/completions` | LIVE |
| 2 | OTel GenAI | 可观测性（真实打点） | `/metrics` | LIVE |
| 3 | AGNTCY SLIM | MLS 消息层（ECDH+KeySchedule+SecretTree+RatchetTree） | `/v1/slim/handshake` `/v1/slim/group` `/v1/slim/tree` | LIVE |
| 4 | MLS 组消息加密 | AES-256-GCM 组密钥传输 | `/v1/slim/message/encrypt\|decrypt` | LIVE |
| 5 | A2A | Agent2Agent（AgentCard / 任务 8 态） | `/v1/a2a/kunlun/dispatch` | LIVE |
| 6 | MCP | Model Context Protocol（工具注册表 / tools call） | `/v1/mcp/kunlun` | LIVE |
| 7 | DPoP | RFC 9449 令牌绑定（jkt 指纹 / 防重放 / 吊销） | `/v1/dpop/verify` `/v1/kunlun/secure` | LIVE |
| 8 | Flower | 联邦学习（FedAvg / SecureAgg） | `/v1/federated/aggregate` `/v1/federated/status` | LIVE |
| 9 | 昆仑生产协议 | 批量生产 / 资产加密 / 锁档 | `/v1/kunlun/production` | LIVE |
| 10 | 四协议联邦组合流 | DPoP→A2A→MCP→SLIM 单请求闭环 | `/v1/federated/kunlun` | LIVE |
| 11 | OAuth2/OIDC | RFC 6749 + 7662 + 7009 + OIDC Discovery | `/.well-known/openid-configuration` `/v1/oauth/token` | LIVE |
| 12 | SSE / WebSocket | 流式输出 / 双向通道（V2.2 新增） | `/v1/chat/stream` `/v1/ws/info` | LIVE |

## 三、协议栈六层架构

```
┌──────────────────────────────────────────────┐
│ L5 可观测层    OTel GenAI /metrics 真实打点    │
├──────────────────────────────────────────────┤
│ L4 认证安全层  DPoP(RFC9449) 令牌绑定/防重放   │
├──────────────────────────────────────────────┤
│ L3 工具执行层  MCP tools/call + 昆仑生产协议    │
├──────────────────────────────────────────────┤
│ L2 编排调度层  A2A AgentCard 任务分发/8态流转   │
├──────────────────────────────────────────────┤
│ L1 传输安全层  SLIM(MLS) 组密钥 AES-256-GCM    │
├──────────────────────────────────────────────┤
│ L0 兼容基座    OpenAI API 兼容 + 模型格式      │
└──────────────────────────────────────────────┘
```

## 四、四协议联邦组合流（单请求闭环）

```
外部Agent ──DPoP令牌──> /v1/federated/kunlun
   环节1 DPoP 认证 ──passed──> 环节2 A2A 编排 ──passed
   ──> 环节3 MCP 执行 ──passed──> 环节4 SLIM 加密 ──passed
   产出: MLS AES-256-GCM 加密 | 审计: runs 落盘可回溯
```

## 五、公网验证基线

- compat version 2.2.0（十二协议族全 LIVE）
- 组合流 4/4 环节 passed、未授权调用 401 拦截、jkt 不匹配 401、吊销后 401
- 全量自检 PASS、L1 巡检基线收敛

## 六、对外入口矩阵

| 入口 | 地址 |
|---|---|
| 体系落地页（官网） | https://www.huodouai.com/zongyuan/ |
| 技术白皮书库（官网） | https://www.huodouai.com/whitepaper/ |
| 本数据湖（魔搭） | https://modelscope.cn/datasets/zongyuanroot/ZONGYUAN-SHARED-DATALAKE |
| 开放知识库 | https://modelscope.cn/datasets/zongyuanroot/zongyuan-root-open-knowledge |
| AtomGit 镜像 | https://atomgit.com/zongyuangen/ZONGYUAN-SHARED-DATALAKE |
| 兼容层源码（kernel） | `kernel/zr_compat_bridge.py`（本仓库内） |

## 七、仓库导航

- `whitepapers/series/ZONGYUAN-通用协议全面兼容白皮书-V2.2.md` — 白皮书全文（MD）
- `whitepapers/series/ZONGYUAN-通用协议全面兼容白皮书-V2.2.html` — 白皮书全文（HTML）
- `gpu-agent/` — GPU 联邦 Agent 运行时
- `kernel/zr_compat_bridge.py` — 兼容层内核（12 协议族算子）
- `meta-rules/` — 元法则/元规则
- `README-SERIES-INDEX.md` — 全系列白皮书索引

---

*ZONGYUAN-ROOT · 元极恒一 · 通用协议全面兼容层 V2.2 · 魔搭数据湖 + AtomGit 双对外展示*
