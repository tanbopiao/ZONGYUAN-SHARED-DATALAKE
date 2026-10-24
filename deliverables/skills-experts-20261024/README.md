# ZONGYUAN-ROOT 技能与专家交付物 · 2026-10-24

> DID-BR-000002 ｜ Ω₀⊂⊙∞⊂Ω ｜ 批次：自洽AI工程坊 v1.1.0 + 造枢 v1.0.1（revision 2）

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
| 13 | `skill-and-expert-pipeline.zip` | 造枢技能：技能&专家全流程制作（含自带预检脚本） |

### 专家插件包（experts/，2 个）

| # | 插件包 | 类型 | 说明 |
|---|---|---|---|
| 1 | `自洽AI工程坊_v1.1.0.zip` | team 型（8 agent + 11 技能） | 企业应用自治创建专家团：坊主 + 规/启/忆/环/封/衡/俭七席 |
| 2 | `造枢_v1.0.1.zip` | agent 型（1 agent + 1 技能） | 技能&专家全流程制作专家（craft-master，资产包完全自包含） |

逐文件 sha256 见 `MANIFEST.json`；上传操作步骤见 `上传指引.md`。

## 二、版本修订记录

| 修订 | 时间 | 内容 |
|---|---|---|
| rev 2 | 2026-10-24 20:5x | 造枢 v1.0.0 → **v1.0.1**：修复平台审核驳回「资产包缺少必需资源 2 项」（引用了包外技能 expert-manager 及其 scripts/validate_expert.py）。修复：① 清除全部对外部技能的从属引用（改为平台内置工具名描述）② 预检能力内联为包内 `scripts/precheck_expert_pack.py`（零依赖，复刻官方校验核心断言）③ 新增「资产包自包含铁律」写入 SKILL.md 与 expert-plugin-contract.md。修复后：自带预检 17 PASS / 官方校验 0 error 0 warning / 平台复刻预检 1/1 / 模拟审核复扫 CLEAN。 |
| rev 1 | 2026-10-24 20:0x | 首次上线：15 包推 ModelScope / AtomGit×2 / GitHub / Gitee 五平台，全量回读校验 ALL-IDENTICAL。 |

## 三、平台落点（单一真相源）

| 平台 | 仓库 | 分支 |
|---|---|---|
| ModelScope 魔搭 | zongyuanroot/zongyuan-whitepaper | master |
| AtomGit 主湖 | zongyuangen/huodouai | main |
| AtomGit 共享湖 | zongyuangen/ZONGYUAN-SHARED-DATALAKE | master |
| GitHub | tanbopiao/ZONGYUAN-SHARED-DATALAKE | main |
| Gitee | huodou-cloud-intelligence-aios/ZONGYUAN-SHARED-DATALAKE | master |
| CNB | zongyuanroot/zongyuanroot | main（阻塞：令牌缺 repo-code:rw） |
| 百度 AI Studio | zongyuan-whitepaper（未建仓） | master（阻塞：待手动建仓） |

（提交号以当日《技能与专家交付物上线报告_20261024.md》与 PUSH_REPORT.json 为准；rev 2 更新提交见报告 revision 节。）

## 四、纪律

- 资产包自包含：包内引用只准指向包内资源，禁止「某外部技能的 scripts/xxx」式从属引用（平台审核会判缺少必需资源整包驳回）
- 上传前四门禁：自带预检 → 官方 validate_expert → 平台复刻预检（zip）→ 模拟审核复扫（解包 grep 外部引用）
- 凭据扫描 8 类模式，命中即人工复核
