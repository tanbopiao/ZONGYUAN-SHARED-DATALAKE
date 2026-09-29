import http.server, json, uuid, os, time, threading, sqlite3, urllib.request
from datetime import datetime

DB="/www/wwwroot/www.huodouai.com/api/tasks.db"
ZHIPU_KEY="d63c880c0e1b424d8ad242f686e83451.vhHr5d5OQUY5UHNp"
AGNES_KEY="sk-c15ub0rOGZXa33elApicuNCvyLXXqzRYQY8U7nlzjxSrzywv"
# 角色基准图（作品库已有的高质量图）
BASE_IMAGES={
  "西王母":["https://www.huodouai.com/gallery/rose/assets/thumbs/02_xiwangmu_2515.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/02_xiwangmu_2821.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/02_xiwangmu_7960.webp"],
  "九天玄女":["https://www.huodouai.com/gallery/rose/assets/thumbs/01_jiutian_6235.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/01_jiutian_650.webp"],
  "太阴月神":["https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_red_goddess_01_lotus.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_red_goddess_02_gold.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_red_goddess_03_phoenix.webp"],
  "九尾狐":["https://www.huodouai.com/gallery/rose/assets/thumbs/03_jiuweihu_2122.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/03_jiuweihu_7083.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/03_jiuweihu_8531.webp"],
  "瑶姬":["https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_yaoji_01_linfan.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_yaoji_02_buyu.webp","https://www.huodouai.com/gallery/rose/assets/thumbs/kunlun_yaoji_03_huimou.webp"]
}

def init_db():
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,role TEXT,theme TEXT,episodes INT,status TEXT,progress INT,created TEXT,download TEXT,outline TEXT,mode TEXT)")
    c.commit();c.close()

def save_task(t):
    c=sqlite3.connect(DB)
    c.execute("INSERT OR REPLACE INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?)",(t["id"],t["role"],t["theme"],t["episodes"],t["status"],t["progress"],t["created"],t.get("download",""),t.get("outline",""),t.get("mode","")))
    c.commit();c.close()

def load_tasks():
    c=sqlite3.connect(DB)
    rows=c.execute("SELECT * FROM tasks ORDER BY created DESC LIMIT 20").fetchall()
    c.close()
    return [dict(zip(["id","role","theme","episodes","status","progress","created","download","outline","mode"],r)) for r in rows]

def load_task(tid):
    c=sqlite3.connect(DB)
    r=c.execute("SELECT * FROM tasks WHERE id=?",(tid,)).fetchone()
    c.close()
    if r: return dict(zip(["id","role","theme","episodes","status","progress","created","download","outline","mode"],r))
    return None

def call_zhipu(prompt):
    try:
        data=json.dumps({"model":"glm-4-flash","messages":[{"role":"user","content":prompt}]}).encode()
        req=urllib.request.Request("https://open.bigmodel.cn/api/paas/v4/chat/completions",data=data,headers={"Authorization":"Bearer "+ZHIPU_KEY,"Content-Type":"application/json"})
        r=urllib.request.urlopen(req,timeout=60)
        return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return "大纲生成失败:"+str(e)

def call_agnes_image(prompt, ref_url=None, key=None):
    try:
        k=key or AGNES_KEY
        body={"model":"agnes-image-2.0-flash","prompt":prompt,"n":1,"size":"1024x1792"}
        if ref_url: body["image"]=ref_url
        data=json.dumps(body).encode()
        req=urllib.request.Request("https://apihub.agnes-ai.com/v1/images/generations",data=data,headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"})
        r=urllib.request.urlopen(req,timeout=120)
        return json.loads(r.read())
    except Exception as e:
        return {"error":str(e)}

def call_agnes_video(prompt, image_url=None, key=None, extra_images=None):
    try:
        k=key or AGNES_KEY
        body={"model":"agnes-video-v2.5","prompt":prompt,"num_frames":81,"frame_rate":24,"width":576,"height":1024,"negative_prompt":"western fantasy, medieval europe, modern city, guns, cars, modern clothes, ugly, blurry, deformed, cartoon, anime"}
        if image_url: body["image"]=image_url
        if extra_images: body["extra_body"]={"image":extra_images,"mode":"keyframes"}
        data=json.dumps(body).encode()
        req=urllib.request.Request("https://apihub.agnes-ai.com/v1/videos",data=data,headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"})
        r=urllib.request.urlopen(req,timeout=30)
        return json.loads(r.read())
    except Exception as e:
        return {"error":str(e)}

def poll_agnes(video_id, key=None):
    k=key or AGNES_KEY
    for _ in range(60):
        try:
            req=urllib.request.Request("https://apihub.agnes-ai.com/agnesapi?video_id="+video_id,headers={"Authorization":"Bearer "+k})
            r=urllib.request.urlopen(req,timeout=15)
            d=json.loads(r.read())
            if d.get("status")=="completed":
                return d.get("url") or d.get("metadata",{}).get("url","")
            if d.get("status")=="failed":
                return ""
        except: pass
        time.sleep(5)
    return ""

init_db()

class H(http.server.BaseHTTPRequestHandler):
    def _c(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self):
        self.send_response(200);self._c();self.end_headers()
    def do_POST(self):
        if self.path=="/api/produce":
            ln=int(self.headers["Content-Length"])
            b=json.loads(self.rfile.read(ln))
            tid=str(uuid.uuid4())[:8]
            t={"id":tid,"role":b.get("role",""),"theme":b.get("theme",""),"episodes":b.get("episodes",1),"status":"排队中","progress":0,"created":datetime.now().isoformat(),"mode":b.get("mode","free")}
            save_task(t)
            threading.Thread(target=_run,args=(tid,b.get("role",""),b.get("theme",""),b.get("mode","free"),b.get("api_key","")),daemon=True).start()
            self.send_response(200);self._c();self.send_header("Content-Type","application/json");self.end_headers()
            self.wfile.write(json.dumps({"task_id":tid}).encode())
    def do_GET(self):
        if self.path.startswith("/api/task/"):
            tid=self.path.split("/")[-1]
            t=load_task(tid) or {"error":"not found"}
        elif self.path=="/api/tasks":
            t=load_tasks()
        else: t={}
        self.send_response(200);self._c();self.send_header("Content-Type","application/json");self.end_headers()
        self.wfile.write(json.dumps(t).encode())

def _run(tid,role,theme,mode,user_key):
    key=user_key if mode=="bring_key" else None
    # Step 1: 大纲
    t=load_task(tid);t["status"]="写大纲";t["progress"]=10;save_task(t)
    outline=call_zhipu("昆仑洞天国风短剧：写一个1分钟竖屏短剧大纲，角色："+role+"，主题："+theme+"。要求：华夏上古神话东方美学，不要西方奇幻，不要现代元素。输出3个关键场景，每场景一句话。")
    t=load_task(tid);t["outline"]=outline[:400];save_task(t)
    # Step 2: 分镜
    t=load_task(tid);t["status"]="拆分镜";t["progress"]=25;save_task(t)
    time.sleep(1)
    # Step 3: 直接用作品库基准图作为关键帧（符合昆仑洞天天元法则）
    t=load_task(tid);t["status"]="加载基准帧";t["progress"]=45;save_task(t)
    import random
    refs=BASE_IMAGES.get(role,[""])
    keyframe_url=random.choice(refs)
    t=load_task(tid)
    t["outline"]+=" | 基准帧:"+keyframe_url[:60]
    save_task(t)
    # Step 4: 视频（2个镜头拼接，以基准图为首帧）
    t=load_task(tid);t["status"]="渲染镜头1";t["progress"]=65;save_task(t)
    RULES="Chinese ancient mythology, Kunlun Xianxia aesthetic, Hanfu, Eastern goddess, ink wash, gold and jade tones, no western fantasy, no modern clothes, no modern buildings, no guns, no cars"
    vres1=call_agnes_video(role+" in "+theme+", 9:16 vertical, slow cinematic establishing shot, "+RULES, keyframe_url or None, key, refs)
    url1=poll_agnes(vres1["video_id"], key) if "video_id" in vres1 else ""
    t=load_task(tid);t["status"]="渲染镜头2";t["progress"]=80;save_task(t)
    vres2=call_agnes_video(role+" in "+theme+", 9:16 vertical, close up emotional, hair and silk flowing in wind, "+RULES, keyframe_url or None, key, refs)
    url2=poll_agnes(vres2["video_id"], key) if "video_id" in vres2 else ""
    # Step 5: 拼接+下载
    local_url=""
    try:
        os.makedirs("/www/wwwroot/www.huodouai.com/produced",exist_ok=True)
        d="/www/wwwroot/www.huodouai.com/produced/"+tid
        os.makedirs(d,exist_ok=True)
        v1=d+"/v1.mp4"; v2=d+"/v2.mp4"; out="/www/wwwroot/www.huodouai.com/produced/"+tid+".mp4"
        if url1: urllib.request.urlretrieve(url1,v1)
        if url2: urllib.request.urlretrieve(url2,v2)
        if os.path.exists(v1) and os.path.exists(v2):
            os.system('ffmpeg -y -i "concat:'+v1+'|'+v2+'" -c copy "'+out+'" 2>/dev/null')
            if os.path.getsize(out)>10000: local_url="/produced/"+tid+".mp4"
            else: local_url="/produced/"+tid+"/v1.mp4"
        elif os.path.exists(v1): local_url="/produced/"+tid+"/v1.mp4"
    except Exception as e: pass
    t=load_task(tid)
    t["status"]="完成" if local_url else "完成(视频待重试)"
    t["progress"]=100
    if local_url: t["download"]=local_url
    save_task(t)
    # 自动通知ntfy群
    try:
        msg="短剧任务%s完成\n角色：%s | 主题：%s\n视频：https://www.huodouai.com%s"%(tid,role,theme,local_url or "失败")
        nd=urllib.request.Request("https://ntfy.sh/zongyuan-kunlun-2026-result",data=msg.encode(),headers={"Title":"昆仑洞天短剧产线","Priority":"high"})
        urllib.request.urlopen(nd,timeout=5)
    except: pass

if __name__=="__main__":
    http.server.HTTPServer(("127.0.0.1",8899),H).serve_forever()
