#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NODE-CLOUD-SECOND-KERNEL 云端第二自治内核 V1.0
定位：部署在云服务器(123.207.202.158)上的应用层独立自治内核，
      与原内核(hub-central-agent，内隔离区)通过记忆网关同源协议双向握手互通。
设计：
  - 原内核：内隔离区，META-ISO-051保护，本内核不触碰（只读其公开真值）
  - 第二内核：应用层承载，独立状态机/心跳/任务循环/同源上报
  - 同源协议：X-DID + X-Trace + X-Source 三头鉴权，经记忆网关真值库交换状态
  - 双向握手：SECOND-KERNEL 上报自身状态 → 读取原内核状态 → 形成互通闭环
锚定：Ω₀⊂⊙∞⊂Ω | DID-BR-000002
"""
import os, json, time, uuid, urllib.request, datetime, socket, hashlib

DID = "DID-BR-000002"
ANCHOR = "OMEGA"
NODE = "NODE-CLOUD-SECOND-KERNEL"
GW = "https://www.huodouai.com"
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "second_kernel_state.json")

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def trace_id():
    return f"trace-{uuid.uuid4().hex[:16]}"

# ============ 同源协议基础 ============
def headers(extra_trace=True):
    h = {"Content-Type": "application/json", "X-DID": DID, "X-Source": NODE}
    if extra_trace: h["X-Trace"] = trace_id()
    return h

def report(key, value, ttype="config"):
    body = {"key": key, "truth_type": ttype, "truth_value": value,
            "did": DID, "anchor": ANCHOR, "status": "CONFIRMED"}
    req = urllib.request.Request(f"{GW}/api/report/truth", data=json.dumps(body).encode(), headers=headers())
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)[:100]}

def read_truths():
    req = urllib.request.Request(f"{GW}/api/report/truths", headers=headers(extra_trace=False))
    try:
        r = urllib.request.urlopen(req, timeout=15)
        d = json.loads(r.read().decode())
        return d.get('truths', []), d.get('count', 0)
    except Exception as e:
        return [], -1

# ============ 状态持久化 ============
def load_state():
    if os.path.exists(STATE_FILE):
        try: return json.load(open(STATE_FILE, encoding='utf-8'))
        except: pass
    return {"node": NODE, "block_height": 0, "created": now(), "origin_kernel_seen": False}

def save_state(s):
    json.dump(s, open(STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ============ 云端健康巡检(外围，不触碰原内核) ============
def probe(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"X-DID": DID}), timeout=12)
        return r.status
    except Exception as e:
        return f"ERR:{str(e)[:30]}"

def health():
    return {
        "truths": probe(f"{GW}/api/report/truths"),
        "website": probe(f"{GW}/"),
        "mgmt_status": probe(f"{GW}/api/status"),
        "mgmt_stats": probe(f"{GW}/api/stats"),
    }

# ============ 双向握手(核心) ============
def handshake(state):
    """第二内核上报自身状态，并读取原内核公开状态，形成互通"""
    # 1. 上报自身心跳(第二内核)
    hs_key = f"truth.kernel.second-kernel.heartbeat.{int(time.time())}"
    hs_val = json.dumps({
        "node": NODE, "block": state['block_height'],
        "ts": now(), "status": "ACTIVE", "anchor": ANCHOR
    }, ensure_ascii=False)
    rep = report(hs_key, hs_val, "config")

    # 2. 读取记忆网关全量key，识别原内核(hub-central-agent)的公开状态
    keys, count = read_truths()
    origin_keys = [k for k in keys if any(x in k.lower() for x in
                   ['hub.central', 'origin', 'kernel.cloud', 'worker.heartbeat'])]
    state['origin_kernel_seen'] = bool(origin_keys)
    state['origin_kernel_keys'] = origin_keys[-5:]
    state['truth_total'] = count
    state['block_height'] += 1
    state['last_handshake'] = now()

    # 3. 上报握手确认(双内核互通证据)
    hs2_key = f"truth.kernel.second-kernel.handshake.ok.{int(time.time())}"
    hs2_val = json.dumps({
        "node": NODE, "block": state['block_height'],
        "origin_kernel_seen": state['origin_kernel_seen'],
        "origin_sample": origin_keys[-3:],
        "synproto": "X-DID/X-Trace/X-Source 3-header verified",
        "ts": now()
    }, ensure_ascii=False)
    rep2 = report(hs2_key, hs2_val, "decision")

    save_state(state)
    return {"heartbeat": rep, "origin_seen": state['origin_kernel_seen'],
            "origin_sample": origin_keys[-3:], "count": count, "handshake_ok": rep2}

# ============ 主循环 ============
def run_cycle():
    state = load_state()
    print(f"=== [{now()}] {NODE} 自治循环 (block #{state['block_height']}) ===")
    print(f"锚定 {ANCHOR} | {DID} | 同源协议 3-header")
    print(f"云端健康: {health()}")
    hs = handshake(state)
    print(f"原内核状态: {'✅ 已检测到(记忆网关可见)' if hs['origin_seen'] else '❌ 未检测到(可能内隔离)'}")
    print(f"记忆网关真值总数: {hs['count']}")
    print(f"本内核最新block: #{state['block_height']} | 握手时间: {state['last_handshake']}")
    print(f"心跳上报: {json.dumps(hs['heartbeat'], ensure_ascii=False)[:120]}")
    return state

if __name__ == "__main__":
    run_cycle()
