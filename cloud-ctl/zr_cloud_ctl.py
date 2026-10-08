#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZONGYUAN-ROOT · 云端轻量调度主控 (zr_cloud_ctl.py)  V1.0
==========================================================
确权: Ω₀⊂⊙∞⊂Ω | DID-BR-000002 | 协议: NTFY-CONNECT-001
部署: 腾讯云中枢服务器 (huodouai-cloud 123.207.202.158), 旁路, 无损
定位: 轻量调度主控 — 复用现有 worker 联通协议, 零 ms-agent 依赖
      (ms-agent 是编排框架; 本主控只做: 收心跳/发命令/收结果/上报真值/台账)

能力:
  1. 订阅命令主题 → 广播/定向 下发命令给所有在线同源 worker
  2. 订阅结果主题 → 收集 worker online/heartbeat/done 回传, 维护节点表
  3. 云端真值上报 → 复用网关 /api/report/truth (X-DID + token)
  4. 任务台账    → 追加写云端本地 JSONL (不动网关/真值库/官网任何文件)
  5. 健康巡检    → 周期心跳汇总, 输出节点存活表

无损保障:
  - 新端口 9010 (仅 127.0.0.1 监听, 不占 9001/80/443/18080)
  - 不改 gateway_server / scheduler / truth_store / 官网docroot / 现有worker
  - 回滚 = 停掉本进程, 中枢零影响

启动:
  nohup python3 zr_cloud_ctl.py > /www/wwwroot/huodouai.com/zhongshu/msagent-ctl.log 2>&1 &
"""
import json, os, sys, time, threading, subprocess, socket, signal
import urllib.request, urllib.error

# ============ 协议复用 (同目录优先) ============
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# 云端协议包路径: 从本地 /home/user/ZONGYUAN-ROOT/07_代码与脚本/ 同步
PROTO_DIR = "/www/wwwroot/huodouai.com/zhongshu/zhongshu-server"
for _p in [_HERE, PROTO_DIR]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from zr_node_protocol import (
        PROTO, DID, MAIN_TOPIC, RESULT_TOPIC, SCAN_TOPIC, NTFY_BASE,
        encode_cmd, decode_msg, is_trusted, check_safe,
    )
except Exception as e:
    print(f"[协议加载失败] {e} — 内置兜底常量", flush=True)
    PROTO, DID = "NTFY-CONNECT-001", "DID-BR-000002"
    MAIN_TOPIC, RESULT_TOPIC, SCAN_TOPIC = "zongyuan-kunlun-2026", "zongyuan-kunlun-2026-result", "zongyuan-kunlun-2026-scan"
    NTFY_BASE = "https://ntfy.sh"
    def encode_cmd(cmd, src="ZR-CLOUD-CTL-001", timeout=300, task_id=None, node=None):
        import uuid
        m = {"proto": PROTO, "zr_did": DID, "src": src,
             "task_id": task_id or f"t-{int(time.time())}-{uuid.uuid4().hex[:6]}",
             "cmd": cmd, "timeout": timeout, "type": "cmd"}
        if node: m["node"] = node
        return json.dumps(m, ensure_ascii=False)
    def decode_msg(raw):
        try: return json.loads(raw)
        except Exception: return None
    def is_trusted(m): return isinstance(m, dict) and m.get("proto") == PROTO and m.get("zr_did") == DID
    def check_safe(cmd): return (True, "ok")

# ============ 配置 ============
HUB_CTL = "ZR-CLOUD-CTL-001"
CONTROL_PORT = 9010
CTL_BIND = "127.0.0.1"           # 仅本机, 不对外
CTL_TOKEN = os.environ.get("ZR_CTL_TOKEN", "ZR-CTL-2026-OMEGA")  # 本地控制面 token
LEDGER_FILE = "/www/wwwroot/huodouai.com/zhongshu/data/msagent-ctl-ledger.jsonl"
NODE_TABLE_FILE = "/www/wwwroot/huodouai.com/zhongshu/data/msagent-nodes.json"
CACHE_TS = int(time.time())

# 云端真值上报
TRUTH_API = os.environ.get("ZR_TRUTH_API", "https://www.huodouai.com/api/report/truth")
X_TOKEN = os.environ.get("ZR_TOKEN", "")
DID_HEADER = DID

# ============ 工具 ============
def now():
    return int(time.time())

def jload(p):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return None

def ledger_append(obj):
    try:
        os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
        with open(LEDGER_FILE, "a") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        print(f"[台账写入失败] {e}", flush=True); return False

def ntfy_pub(topic, text):
    try:
        req = urllib.request.Request(f"{NTFY_BASE}/{topic}", data=text.encode(),
                                     headers={"Content-Type": "text/plain"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except Exception as e:
        print(f"[ntfy发布失败] {e}", flush=True); return None

def report_truth(key, value_json):
    """上报云端真值中枢 (与 zr_node_protocol.report_truth 一致)"""
    try:
        body = json.dumps({"truth_key": key, "truth_value": value_json,
                           "source_node": HUB_CTL, "truth_type": "rule",
                           "confidence": 0.95}, ensure_ascii=False).encode()
        req = urllib.request.Request(TRUTH_API, data=body, headers={
            "X-Capture-Token": X_TOKEN, "X-DID": DID_HEADER,
            "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ============ 节点表 & 心跳 ============
NODES = {}   # node -> {"last_ts", "last_heartbeat", "gpu", "out"}

def note_event(msg):
    node = msg.get("node", "?")
    NODES[node] = {
        "last_ts": now(), "type": msg.get("type", "?"),
        "gpu": msg.get("gpu", ""), "last_out": str(msg.get("out", ""))[:200],
        "task_id": msg.get("task_id", ""),
    }
    _persist_nodes()

def _persist_nodes():
    try:
        os.makedirs(os.path.dirname(NODE_TABLE_FILE), exist_ok=True)
        with open(NODE_TABLE_FILE, "w") as f:
            json.dump({"updated_ts": now(), "nodes": NODES}, f, ensure_ascii=False, indent=2)
    except Exception: pass

# ============ ntfy 订阅线程 ============
def sub_thread(topic, handler, tag):
    """长轮询订阅 ntfy topic; 收到消息 → handler(json or text)"""
    while True:
        try:
            url = f"{NTFY_BASE}/{topic}/json?poll=1&since={CACHE_TS}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as r:
                while True:
                    raw = r.readline()
                    if not raw:
                        break
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line: continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("event") == "message":
                        handler(d.get("message", ""))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10)  # 限流退避
            else:
                time.sleep(5)
        except Exception as e:
            print(f"[{tag}] 断开: {str(e)[:80]} | 5s后重连", flush=True)
            time.sleep(5)

def on_result(raw):
    msg = decode_msg(raw)
    if msg is None: return
    if not is_trusted(msg): return
    note_event(msg)
    if msg.get("type") == "online":
        print(f"[上线] {msg.get('node')} | gpu={msg.get('gpu','?')}", flush=True)
    elif msg.get("type") == "heartbeat":
        pass  # 心跳仅更新节点表
    elif msg.get("type") == "done":
        print(f"[完成] {msg.get('node')} | {msg.get('task_id','')} code={msg.get('code','?')}", flush=True)

# ============ 命令下发 ============
def send_cmd(cmd, node=None, task_id=None, src=HUB_CTL, timeout=300):
    payload = encode_cmd(cmd, src=src, timeout=timeout, task_id=task_id, node=node)
    st = ntfy_pub(MAIN_TOPIC, payload)
    ok = st in (200, 201)
    ledger_append({"ts": now(), "op": "cmd", "cmd": cmd[:100], "node": node or "*",
                   "task_id": task_id or "", "publish_status": st, "ok": ok})
    return ok

def snapshot():
    """节点存活快照: 计算30s内心跳的在线节点"""
    t = now()
    online = [n for n, d in NODES.items() if t - d["last_ts"] <= 60]
    return {"ts": t, "online_count": len(online), "online": online,
            "total_seen": len(NODES), "nodes": {n: d for n, d in NODES.items()}}

# ============ HTTP 控制面 (仅127.0.0.1:9010) ============
def ctl_handler():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class H(BaseHTTPRequestHandler):
        def _auth(self):
            return self.headers.get("X-CTL-Token", "") == CTL_TOKEN
        def _json(self, code, obj):
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        def do_GET(self):
            if not self._auth():
                return self._json(403, {"ok": False, "error": "bad token"})
            if self.path.startswith("/health"):
                g = jload(NODE_TABLE_FILE) or {}
                self._json(200, {"ok": True, "ctl": HUB_CTL, "ledger": LEDGER_FILE,
                                 "nodes": g.get("nodes", {}), "snapshot": snapshot()})
            elif self.path.startswith("/nodes"):
                self._json(200, snapshot())
            else:
                self._json(404, {"ok": False, "error": "not found"})
        def do_POST(self):
            if not self._auth():
                return self._json(403, {"ok": False, "error": "bad token"})
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n) if n else b"{}"
            try: data = json.loads(body.decode())
            except Exception: data = {}
            if self.path.startswith("/cmd"):
                cmd = data.get("cmd", "")
                node = data.get("node")
                ok = send_cmd(cmd, node=node, task_id=data.get("task_id"),
                              timeout=data.get("timeout", 300))
                self._json(200, {"ok": ok, "sent": cmd[:100], "node": node or "*",
                                 "nodes_online": len(snapshot()["online"])})
            elif self.path.startswith("/report"):
                r = report_truth(data.get("key", ""), json.dumps(data.get("value", {})))
                self._json(200, {"report": r})
            else:
                self._json(404, {"ok": False, "error": "not found"})
        def log_message(self, *a): pass
    try:
        srv = HTTPServer((CTL_BIND, CONTROL_PORT), H)
        print(f"[控制面] 监听 {CTL_BIND}:{CONTROL_PORT} | token 已设", flush=True)
        srv.serve_forever()
    except Exception as e:
        print(f"[控制面启动失败] {e}", flush=True)

# ============ 心跳巡检线程 (上报) ============
def watchdog_thread():
    while True:
        time.sleep(30)
        snap = snapshot()
        online = snap["online"]
        if online:
            report_truth(f"REPORT.CLOUD-CTL.{now()}",
                         json.dumps({"ctl": HUB_CTL, "online_nodes": online,
                                     "online_count": snap["online_count"]}))
            print(f"[巡检] 在线节点: {online}", flush=True)

def main():
    print(f"ZR 云端主控启动 | {HUB_CTL} | proto={PROTO} | 订阅 {MAIN_TOPIC}/{RESULT_TOPIC}",
          flush=True)
    print(f"网关健康: {report_truth('REPORT.CLOUD-CTL.BOOT.'+str(now()), json.dumps({'boot': True}))}",
          flush=True)
    threading.Thread(target=sub_thread, args=(RESULT_TOPIC, on_result, "result"), daemon=True).start()
    threading.Thread(target=sub_thread, args=(MAIN_TOPIC, lambda raw: None, "cmd-scan"), daemon=True).start()
    threading.Thread(target=ctl_handler, daemon=True).start()
    threading.Thread(target=watchdog_thread, daemon=True).start()
    signal.pause()

if __name__ == "__main__":
    main()
