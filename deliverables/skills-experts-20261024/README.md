# ZONGYUAN-ROOT 技能与专家交付物 · 2026-10-24

> DID-BR-000002 ｜ Ω₀⊂⊙∞⊂Ω ｜ 批次：自洽AI工程坊 v1.1.0 + 造枢 v1.0.0

本目录为「企业应用创建专家团（自洽AI工程坊）」与「造枢（技能&专家全流程制作专家）」
两套交付物的正式发布包，包含 **13 个技能包 + 2 个专家插件包**，全部经官方校验
（0 error 0 warning）与凭据扫描（0 命中）。

## 一、交付物清单

### 技能包（skills/，13 个）

| # | 技能包 | 说明 |
|---|---|---|
| 1 | `self-consistent-ai-forge.zip` | **集成包**：自洽AI工程坊 11 技能合辑（主 SKILL.md 路由 + references 渐进式披露） |
| 2 | `autonomous-runtime.zip` | 自治运行时装配 |
| 3 | `deterministic-bootstrap.zip` | 确定性引导 |
| 4 | `engineering-maturity-audit.zip` | 工程化成熟度审计 |
| 5 | `federated-memory-sync.zip` | 联邦记忆同步 |
| 6 | `global-hash-lockdown.zip` | 全域哈希锁档 |
| 7 | `layered-autonomy-architect.zip` | 分层自治架构 |
| 8 | `single-source-governance.zip` | 单一真相源治理 |
| 9 | `stability-discipline.zip` | 稳定性纪律 |
| 10 | `task-closed-loop-bus.zip` | 任务闭环总线 |
| 11 | `verifiability-ci.zip` | 可验证性 CI |
| 12 | `consumption-governance.zip` | 三消耗治理守门（额度/积分/算力，事前预检） |
| 13 | `skill-and-expert-pipeline.zip` | 造枢技能：技能&专家全流程制作 |

### 专家插件包（experts/，2 个）

| # | 插件包 | 类型 | 说明 |
|---|---|---|---|
| 1 | `自洽AI工程坊_v1.1.0.zip` | team 型（8 agent + 11 技能） | 企业应用自治创建专家团：坊主 + 规/启/忆/环/封/衡/俭七席 |
| 2 | `造枢_v1.0.0.zip` | agent 型（1 agent + 1 技能） | 技能&专家全流程制作专家（craft-master） |

逐文件 sha256 见 `MANIFEST.json`；上传操作步骤见 `上传指引.md`。

## 二、平台落点（单一真相源）

| 平台 | 仓库 | 分支 |
|---|---|---|
| ModelScope（魔搭） | `zongyuanroot/zongyuan-whitepaper` | master |
| AtomGit | `zongyuangen/huodouai` | main |
| GitHub | `tanbopiao/ZONGYUAN-SHARED-DATALAKE` | main |
| Gitee | `huodou-cloud-intelligence-aios/ZONGYUAN-SHARED-DATALAKE` | master |
| CNB | `zongyuanroot/zongyuanroot` | master |
| 百度 AI Studio | **待建仓**（Gitea API 关闭，须控制台手动建 `zongyuan-whitepaper`，默认分支 master） | — |

## 三、合规声明

- 全部 zip 经 8 类凭据模式扫描，**0 命中**；
- 技能包 frontmatter 12 字段、平台校验 0 error 0 warning；
- 专家插件按平台 team/agent 契约重构（`.codebuddy-plugin/plugin.json`）；
- 本目录内容可公开分发，不含任何密钥本体。
