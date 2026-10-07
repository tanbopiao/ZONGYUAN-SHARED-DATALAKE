#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zr_node_git.py · modelscope 双向控制面 Worker V1.0 (mode=git-poll)
================================================================
确权: Ω₀⊂⊙∞⊂Ω | DID-BR-000002 | ZR-NODE-DC2E51C0
职责: 实例侧唯一可靠控制面 —— 经 modelscope 共享数据湖 git 双向闭环:
      主控 push CMD-<id>.json → 实例 pull 执行 → push RESULT-<id>.json → 主控 pull 确认
      结果+心跳同步上报云端镜像(自动key, value带标记, 可审计)
通道: modelscope git (双向, 需实例配一次性 push 凭证) + 云端上报(镜像)
流程:
  轮询每30s:
    git pull origin master (control/)        # 取命令
    扫描 CMD-<id>.json (未处理) → 执行 → 写 RESULT-<id>.json
    git add/commit/push                       # 回传结果
    POST 云端 RESULT.<id> (value镜像)
幂等: 处理后删除 CMD 文件 + 本地 done 记录
退避: git/网络错误 5→60s 封顶 (META-STEADY-001-C)
部署: 实例持久层 /mnt/workspace/zr_node_git.py + 凭证 /mnt/workspace/.zr/git_token.env
用法: nohup python3 /mnt/workspace/zr_node_git.py >> /mnt/workspace/git_worker.log 2>&1 &
"""
import json, os, subprocess, time, urllib.request, urllib.error

NODE = os.environ.get("ZR_NODE", "ZR-NODE-MODEL-dsw-223619")
DID = "DID-BR-000002"
REPO_DIR = "/mnt/workspace/zr_ctrl"           # 命令槽工作区(稀疏clone control/)
CTRL_REL = "control"                          # 数据湖内相对目录
TOKEN_FILE = "/mnt/workspace/.zr/node_token.env"
GIT_TOKEN_FILE = "/mnt/workspace/.zr/git_token.env"
REPORT_URL = "https://www.huodouai.com/api/report/truth"
DONE_FILE = "/mnt/workspace/.zr/git_worker_done.json"
GIT_REMOTE = "https://modelscope.cn/datasets/zongyuanroot/ZONGYUAN-SHARED-DATALAKE.git"

def sh(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except Exception as e:
        return -1, "", str(e)

def git_remote_url():
    """带凭证的 remote URL (仅实例本地使用, token存600权限env)"""
    token = ""
    try:
        for line in open(GIT_TOKEN_FILE):
            if line.strip().startswith("ZR_GIT_TOKEN="):
                token = line.strip().split("=", 1)[1].strip()
    except Exception:
        pass
    if not token:
        token = os.environ.get("ZR_GIT_TOKEN", "")
    if token:
        return GIT_REMOTE.replace("https://", f"https://zongyuanroot:{token}@")
    return GIT_REMOTE

def load_token():
    try:
        for line in open(TOKEN_FILE):
            if line.strip().startswith("ZR_NODE_TOKEN="):
                return line.strip().split("=", 1)[1].strip()
    except Exception:
        pass
    return os.environ.get("ZR_NODE_TOKEN", "")

def post_cloud(key, value):
    token = load_token()
    if not token:
        return False
    body = json.dumps({"truth_key": key, "truth_value": value,
                       "source_node": NODE, "truth_type": "rule", "confidence": 0.95},
                      ensure_ascii=False).encode()
    req = urllib.request.Request(REPORT_URL, data=body, headers={
        "X-Capture-Token": token, "X-DID": DID, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return True
    except Exception:
        return False

def load_done():
    try:
        return set(json.load(open(DONE_FILE)))
    except Exception:
        return set()

def save_done(d):
    try:
        json.dump(sorted(d), open(DONE_FILE, "w"))
    except Exception:
        pass

def ensure_repo():
    """初始化/恢复 命令槽稀疏clone"""
    if os.path.isdir(os.path.join(REPO_DIR, ".git")):
        return True
    os.makedirs(os.path.dirname(REPO_DIR), exist_ok=True)
    url = git_remote_url()
    sh(f"rm -rf {REPO_DIR}")
    # 稀疏clone仅control目录
    rc, out, err = sh(f"git clone --depth 1 --filter=blob:none --sparse {url} {REPO_DIR}", 120)
    if rc != 0:
        return False
    sh(f"cd {REPO_DIR} && git sparse-checkout set {CTRL_REL}", 60)
    return True

def git_pull():
    """拉取命令 (fast-forward; 冲突时fetch+checkout --force控制目录)"""
    url = git_remote_url()
    rc, out, err = sh(f"cd {REPO_DIR} && git remote set-url origin '{url}' && git pull --ff-only origin master", 90)
    if rc == 0:
        return True
    # 冲突回退: fetch + checkout --force control/  (只恢复控制目录, 不丢其它)
    rc2, out2, err2 = sh(f"cd {REPO_DIR} && git fetch origin master 2>&1 && git checkout --force FETCH_HEAD -- {CTRL_REL}", 90)
    return rc2 == 0

def git_push(commit_msg):
    url = git_remote_url()
    rc, out, err = sh(f"cd {REPO_DIR} && git remote set-url origin '{url}' && git add -A && git -c user.email='zongyuanroot@modelscope.cn' -c user.name='zongyuanroot' commit -m '{commit_msg}' 2>&1 && git push origin master", 120)
    return rc == 0

def run_cmd(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "")[:1500]
        if r.stderr:
            out += f"\n[stderr] {r.stderr[:200]}"
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return -2, "[TIMEOUT]"
    except Exception as e:
        return -1, f"[ERR] {e}"

done = load_done()
backoff = 5
print(f"[git] 启动 | node={NODE} | 命令槽 {REPO_DIR}", flush=True)
if not ensure_repo():
    print("[git] 命令槽初始化失败(检查git凭证), 退避重试", flush=True)

while True:
    try:
        if not git_pull():
            raise RuntimeError("git pull 失败")
        backoff = 5
        ctrl = os.path.join(REPO_DIR, CTRL_REL)
        if not os.path.isdir(ctrl):
            os.makedirs(ctrl, exist_ok=True)
        # 扫描 CMD-<id>.json
        cmd_files = [f for f in os.listdir(ctrl) if f.startswith("CMD-") and f.endswith(".json")]
        changed = False
        for fn in sorted(cmd_files):
            task_id = fn[len("CMD-"):-len(".json")]
            if task_id in done:
                continue
            try:
                spec = json.load(open(os.path.join(ctrl, fn)))
            except Exception:
                continue
            cmd = spec.get("cmd")
            if not cmd:
                continue
            print(f"[git] 执行 {task_id}: {str(cmd)[:50]}", flush=True)
            code, out = run_cmd(cmd)
            # 写 RESULT-<id>.json
            res = {"task_id": task_id, "node": NODE, "code": code, "out": out, "ts": int(time.time())}
            with open(os.path.join(ctrl, f"RESULT-{task_id}.json"), "w") as f:
                json.dump(res, f, ensure_ascii=False)
            # 删除 CMD (已处理)
            os.remove(os.path.join(ctrl, fn))
            changed = True
            done.add(task_id); save_done(done)
            # 上报云端镜像
            post_cloud(f"RESULT.{task_id}", json.dumps(res, ensure_ascii=False))
            print(f"[git] 结果 {task_id} code={code}", flush=True)
        if changed:
            git_push(f"zr result {int(time.time())}")
        # 心跳上报云端 (value镜像)
        post_cloud("HEARTBEAT", json.dumps({"node": NODE, "event": "heartbeat", "ts": int(time.time())}, ensure_ascii=False))
    except RuntimeError as e:
        print(f"[git] {e} | 退避{backoff}s", flush=True)
        time.sleep(backoff); backoff = min(backoff * 2, 60)
    except Exception as e:
        print(f"[git] {str(e)[:60]} | 退避{backoff}s", flush=True)
        time.sleep(backoff); backoff = min(backoff * 2, 60)
    time.sleep(30)
