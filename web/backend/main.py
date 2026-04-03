"""ScholarFlow Web Backend — PDF upload only, SSE streaming, rate limiting, history."""

from __future__ import annotations

import asyncio
import json
import uuid
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

app = FastAPI(title="ScholarFlow", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
HISTORY_FILE = DATA_DIR / "history.json"
USAGE_FILE = DATA_DIR / "usage.json"

for d in [UPLOAD_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DAILY_LIMIT = 20

tasks_status: dict[str, dict] = {}
sse_queues: dict[str, asyncio.Queue] = {}


# ── JSON helpers ──────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    usage = _load_json(USAGE_FILE)
    today = date.today().isoformat()
    day_data = usage.get(today, {})
    count = day_data.get(ip, 0)
    if count >= DAILY_LIMIT:
        return False, 0
    return True, DAILY_LIMIT - count


def _increment_usage(ip: str):
    usage = _load_json(USAGE_FILE)
    today = date.today().isoformat()
    if today not in usage:
        usage = {today: {}}
    usage[today][ip] = usage[today].get(ip, 0) + 1
    old_dates = [d for d in usage if d != today]
    for d in old_dates:
        del usage[d]
    _save_json(USAGE_FILE, usage)


def _add_history(task_id: str, input_info: str, status: str):
    history = _load_json(HISTORY_FILE)
    records = history.get("records", [])
    records.insert(0, {
        "task_id": task_id,
        "input_info": input_info,
        "input_type": "pdf",
        "status": status,
        "outputs": {},
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    if len(records) > 200:
        records = records[:200]
    history["records"] = records
    _save_json(HISTORY_FILE, history)


def _update_history(task_id: str, status: str, outputs: dict | None = None):
    history = _load_json(HISTORY_FILE)
    for rec in history.get("records", []):
        if rec["task_id"] == task_id:
            rec["status"] = status
            if outputs:
                rec["outputs"] = outputs
            break
    _save_json(HISTORY_FILE, history)


# ── Frontend ──────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return FRONTEND_HTML


# ── API ───────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.3.0"}


@app.get("/api/remaining")
def remaining(request: Request):
    ip = _get_client_ip(request)
    _, left = _check_rate_limit(ip)
    return {"remaining": left, "limit": DAILY_LIMIT}


@app.post("/api/process")
async def process_paper(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    lang: str = Form("zh"),
    verbosity: str = Form("normal"),
    notes_mode: str = Form("deep"),
    outputs: str = Form("summary,slides,beamer,script,notes,mindmap,poster,translate"),
):
    ip = _get_client_ip(request)
    allowed, _ = _check_rate_limit(ip)
    if not allowed:
        return JSONResponse(status_code=429, content={
            "error": f"今日使用次数已达上限 ({DAILY_LIMIT} 次)，请明天再来！"
        })

    if not file or not file.filename or not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "请上传一个 PDF 文件"})

    task_id = str(uuid.uuid4())[:8]
    task_output = OUTPUT_DIR / task_id
    task_output.mkdir(parents=True, exist_ok=True)

    pdf_path = str(UPLOAD_DIR / f"{task_id}_{file.filename}")
    with open(pdf_path, "wb") as f:
        content = await file.read()
        f.write(content)

    _increment_usage(ip)

    sse_queue: asyncio.Queue = asyncio.Queue()
    sse_queues[task_id] = sse_queue
    tasks_status[task_id] = {"status": "processing", "outputs": {}, "progress": "正在准备..."}

    generate_list = [o.strip() for o in outputs.split(",") if o.strip()]
    _add_history(task_id, file.filename, "processing")

    background_tasks.add_task(
        _run_pipeline,
        task_id=task_id,
        pdf_path=pdf_path,
        output_dir=str(task_output),
        lang=lang,
        verbosity=verbosity,
        notes_mode=notes_mode,
        generate=generate_list,
    )

    return {"task_id": task_id, "status": "processing"}


def _run_pipeline(task_id: str, pdf_path: str, output_dir: str,
                  lang: str, verbosity: str, notes_mode: str, generate: list[str]):
    queue = sse_queues.get(task_id)

    def progress_callback(step: str, message: str, pct: int):
        tasks_status[task_id]["progress"] = message
        if queue:
            queue.put_nowait({"step": step, "message": message, "progress": pct})

    try:
        progress_callback("init", "正在启动处理流水线...", 2)
        from scholarflow.pipeline import run_full_pipeline
        results = run_full_pipeline(
            pdf_path=pdf_path,
            output_dir=output_dir,
            lang=lang,
            verbosity=verbosity,
            notes_mode=notes_mode,
            generate=generate,
            progress_callback=progress_callback,
        )
        output_files = {}
        for k, v in results.items():
            p = Path(v)
            if p.exists():
                output_files[k] = p.name
        tasks_status[task_id] = {"status": "completed", "outputs": output_files, "progress": "完成！"}
        _update_history(task_id, "completed", output_files)
        if queue:
            queue.put_nowait({"step": "complete", "message": "全部完成！", "progress": 100, "outputs": output_files})
    except Exception as e:
        error_msg = str(e)
        tasks_status[task_id] = {"status": "error", "error": error_msg, "progress": "出错了"}
        _update_history(task_id, "error")
        if queue:
            queue.put_nowait({"step": "error", "message": error_msg, "progress": -1})


@app.get("/api/stream/{task_id}")
async def stream_progress(task_id: str):
    """SSE endpoint for real-time progress streaming."""
    async def event_generator():
        queue = sse_queues.get(task_id)
        if not queue:
            yield f"data: {json.dumps({'step': 'error', 'message': '任务不存在', 'progress': -1})}\n\n"
            return

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=120)
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'step': 'heartbeat', 'message': '仍在处理中...', 'progress': -1})}\n\n"
                    continue

                yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"

                if msg.get("step") in ("complete", "error"):
                    sse_queues.pop(task_id, None)
                    break
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    if task_id not in tasks_status:
        return JSONResponse(status_code=404, content={"error": "任务不存在"})
    return tasks_status[task_id]


@app.get("/api/history")
def get_history():
    history = _load_json(HISTORY_FILE)
    return {"records": history.get("records", [])}


@app.get("/api/download/{task_id}")
def download_all(task_id: str):
    task_output = OUTPUT_DIR / task_id
    if not task_output.exists():
        return JSONResponse(status_code=404, content={"error": "输出文件不存在"})
    zip_path = OUTPUT_DIR / f"{task_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in task_output.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(task_output))
    return FileResponse(zip_path, filename=f"scholarflow_{task_id}.zip")


@app.get("/api/download/{task_id}/{filename:path}")
def download_file(task_id: str, filename: str):
    fpath = OUTPUT_DIR / task_id / filename
    if not fpath.exists():
        return JSONResponse(status_code=404, content={"error": "文件不存在"})
    return FileResponse(fpath, filename=filename)


# ── Frontend HTML ─────────────────────────────────────────────

FRONTEND_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ScholarFlow - 学术论文一键处理</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--primary:#2563eb;--primary-dark:#1d4ed8;--bg:#f8fafc;--card:#fff;--text:#1e293b;--text-light:#64748b;--border:#e2e8f0;--success:#22c55e;--error:#ef4444;--radius:12px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:20px}
header{text-align:center;padding:40px 20px 20px}
header h1{font-size:2.2em;background:linear-gradient(135deg,var(--primary),#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
header p{color:var(--text-light);font-size:1.05em}
.social-links{display:flex;justify-content:center;gap:16px;margin-top:14px;flex-wrap:wrap}
.social-links a{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:.88em;text-decoration:none;color:var(--text);background:var(--card);border:1px solid var(--border);transition:all .2s}
.social-links a:hover{border-color:var(--primary);color:var(--primary);transform:translateY(-1px);box-shadow:0 2px 8px rgba(37,99,235,.12)}
.quota{text-align:center;margin:16px 0;font-size:.9em;color:var(--text-light)}
.quota span{font-weight:700;color:var(--primary)}
.card{background:var(--card);border-radius:var(--radius);padding:28px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid var(--border)}
.card h2{font-size:1.2em;margin-bottom:18px;display:flex;align-items:center;gap:8px}
.dropzone{border:2px dashed var(--border);border-radius:var(--radius);padding:50px 20px;text-align:center;cursor:pointer;transition:all .2s;background:var(--bg)}
.dropzone:hover,.dropzone.dragover{border-color:var(--primary);background:#eef2ff}
.dropzone p{color:var(--text-light);font-size:.95em}
.dropzone .icon{font-size:2.8em;margin-bottom:10px}
.dropzone .hint{font-size:.82em;color:var(--text-light);margin-top:6px}
.file-name{margin-top:10px;font-size:.92em;color:var(--primary);font-weight:600}
.output-options{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px;margin-bottom:16px}
.output-opt{display:flex;align-items:center;gap:6px;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:.88em;transition:background .15s}
.output-opt:hover{background:var(--bg)}
.output-opt input{accent-color:var(--primary)}
.input-group{margin-bottom:16px}
.input-group label{display:block;font-size:.88em;font-weight:600;margin-bottom:6px;color:var(--text)}
.input-group select{width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:.95em;transition:border-color .2s;background:var(--bg)}
.input-group select:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(37,99,235,.1)}
.submit-btn{width:100%;padding:14px;background:linear-gradient(135deg,var(--primary),#7c3aed);color:#fff;border:none;border-radius:8px;font-size:1.05em;font-weight:600;cursor:pointer;transition:all .2s}
.submit-btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(37,99,235,.3)}
.submit-btn:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
.progress-area{margin-top:16px;display:none}
.progress-bar{height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-bottom:10px}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--primary),#7c3aed);border-radius:4px;width:0;transition:width .4s ease}
.progress-text{font-size:.9em;color:var(--text-light);text-align:center}
.progress-steps{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}
.step-tag{padding:3px 10px;border-radius:12px;font-size:.78em;background:var(--border);color:var(--text-light);transition:all .3s}
.step-tag.done{background:#dcfce7;color:#166534}
.step-tag.active{background:#dbeafe;color:#1d4ed8;font-weight:600}
.result-area{display:none;margin-top:16px}
.result-files{display:grid;gap:8px}
.result-file{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:var(--bg);border-radius:8px;border:1px solid var(--border)}
.result-file .name{font-size:.92em;font-weight:500}
.result-file .dl-btn{padding:5px 14px;background:var(--primary);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.85em;text-decoration:none;transition:background .2s}
.result-file .dl-btn:hover{background:var(--primary-dark)}
.dl-all-btn{display:block;width:100%;margin-top:12px;padding:12px;background:linear-gradient(135deg,var(--success),#16a34a);color:#fff;border:none;border-radius:8px;font-size:.95em;font-weight:600;cursor:pointer;text-align:center;text-decoration:none}
.dl-all-btn:hover{box-shadow:0 4px 12px rgba(34,197,94,.3)}
.history-list{max-height:400px;overflow-y:auto}
.history-item{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid var(--border);gap:10px;flex-wrap:wrap}
.history-item:last-child{border-bottom:none}
.history-info{flex:1;min-width:0}
.history-info .title{font-size:.92em;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.history-info .meta{font-size:.8em;color:var(--text-light);margin-top:2px}
.status-badge{padding:3px 10px;border-radius:12px;font-size:.78em;font-weight:600;white-space:nowrap}
.status-processing{background:#fef3c7;color:#92400e}
.status-completed{background:#dcfce7;color:#166534}
.status-error{background:#fee2e2;color:#991b1b}
.history-actions a{padding:5px 12px;background:var(--primary);color:#fff;border-radius:6px;font-size:.82em;text-decoration:none}
.error-msg{color:var(--error);font-size:.9em;margin-top:8px;padding:10px;background:#fee2e2;border-radius:8px;display:none}
.footer{text-align:center;padding:30px 20px;color:var(--text-light);font-size:.85em}
@media(max-width:600px){header h1{font-size:1.6em}.output-options{grid-template-columns:1fr 1fr}.container{padding:12px}}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>ScholarFlow</h1>
  <p>上传论文 PDF，一键生成 PPT、笔记、思维导图、海报等全套学术材料</p>
  <div class="social-links">
    <a href="https://github.com/bcefghj/scholarflow" target="_blank">
      <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      GitHub
    </a>
    <a href="https://www.xiaohongshu.com/user/profile/bcefghj" target="_blank">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
      小红书: bcefghj
    </a>
  </div>
</header>

<div class="quota">今日剩余次数: <span id="remaining">--</span> / 20</div>

<div class="card">
  <h2>上传论文 PDF</h2>
  <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
    <div class="icon">📄</div>
    <p>点击选择或拖拽 PDF 文件到这里</p>
    <div class="hint">支持任意学术论文 PDF，文件大小不超过 50MB</div>
    <div class="file-name" id="fileName"></div>
  </div>
  <input type="file" id="fileInput" accept=".pdf" style="display:none" onchange="handleFileSelect(this)">

  <div style="margin:18px 0 16px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div class="input-group" style="margin:0"><label>输出语言</label><select id="optLang"><option value="zh" selected>中文</option><option value="en">English</option></select></div>
    <div class="input-group" style="margin:0"><label>笔记模式</label><select id="optNotes"><option value="deep">深度学习</option><option value="exam">考试复习</option><option value="quick">快速笔记</option><option value="grandma">老奶奶讲解</option></select></div>
  </div>

  <h2 style="font-size:1.05em;margin-bottom:12px">选择输出</h2>
  <div class="output-options">
    <label class="output-opt"><input type="checkbox" value="summary" checked> 简要介绍</label>
    <label class="output-opt"><input type="checkbox" value="slides" checked> 汇报PPT</label>
    <label class="output-opt"><input type="checkbox" value="beamer" checked> Beamer</label>
    <label class="output-opt"><input type="checkbox" value="script" checked> 讲解稿</label>
    <label class="output-opt"><input type="checkbox" value="notes" checked> 学习笔记</label>
    <label class="output-opt"><input type="checkbox" value="mindmap" checked> 思维导图</label>
    <label class="output-opt"><input type="checkbox" value="poster" checked> 学术海报</label>
    <label class="output-opt"><input type="checkbox" value="translate" checked> 双语翻译</label>
  </div>
  <button class="submit-btn" id="submitBtn" onclick="submitTask()">开始处理</button>
  <div class="error-msg" id="errorMsg"></div>
  <div class="progress-area" id="progressArea">
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="progress-text" id="progressText">正在准备...</div>
    <div class="progress-steps" id="progressSteps"></div>
  </div>
  <div class="result-area" id="resultArea">
    <h2 style="font-size:1.05em;margin-bottom:12px">处理完成</h2>
    <div class="result-files" id="resultFiles"></div>
  </div>
</div>

<div class="card">
  <h2>历史记录</h2>
  <div class="history-list" id="historyList"><p style="color:var(--text-light);text-align:center;padding:20px">加载中...</p></div>
</div>

<footer class="footer">ScholarFlow — 学术论文一键处理工具 · <a href="https://github.com/bcefghj/scholarflow" target="_blank" style="color:var(--primary)">GitHub</a></footer>
</div>

<script>
let selectedFile=null;
const STEP_LABELS={parsing:'解析PDF',summary:'简要介绍',slides_content:'PPT内容',slides:'构建PPT',beamer:'Beamer',script:'讲解稿',notes:'学习笔记',mindmap:'思维导图',poster:'学术海报',translate:'双语翻译'};
const OUTPUT_LABELS={summary:'简要介绍',slides:'汇报PPT',beamer:'Beamer',script:'讲解稿',notes:'学习笔记',mindmap:'思维导图',poster:'学术海报',translate:'双语翻译'};

function handleFileSelect(i){if(i.files.length>0){selectedFile=i.files[0];document.getElementById('fileName').textContent=selectedFile.name}}
function handleDrop(e){e.preventDefault();document.getElementById('dropzone').classList.remove('dragover');if(e.dataTransfer.files.length>0&&e.dataTransfer.files[0].name.endsWith('.pdf')){selectedFile=e.dataTransfer.files[0];document.getElementById('fileName').textContent=selectedFile.name}}
function handleDragOver(e){e.preventDefault();document.getElementById('dropzone').classList.add('dragover')}
function handleDragLeave(){document.getElementById('dropzone').classList.remove('dragover')}

async function submitTask(){
  const btn=document.getElementById('submitBtn'),errEl=document.getElementById('errorMsg'),progArea=document.getElementById('progressArea'),resultArea=document.getElementById('resultArea');
  errEl.style.display='none';resultArea.style.display='none';
  if(!selectedFile){errEl.textContent='请先选择一个 PDF 文件';errEl.style.display='block';return}
  const outputs=[...document.querySelectorAll('.output-options input:checked')].map(c=>c.value).join(',');
  if(!outputs){errEl.textContent='请至少选择一种输出';errEl.style.display='block';return}
  const fd=new FormData();
  fd.append('file',selectedFile);
  fd.append('lang',document.getElementById('optLang').value);
  fd.append('notes_mode',document.getElementById('optNotes').value);
  fd.append('outputs',outputs);
  btn.disabled=true;btn.textContent='处理中...';
  progArea.style.display='block';
  document.getElementById('progressFill').style.width='2%';
  document.getElementById('progressText').textContent='正在上传 PDF...';
  document.getElementById('progressSteps').innerHTML='';
  const completedSteps=new Set();
  try{
    const res=await fetch('/api/process',{method:'POST',body:fd});
    if(!res.ok){const d=await res.json();throw new Error(d.error||'提交失败')}
    const{task_id}=await res.json();
    const es=new EventSource('/api/stream/'+task_id);
    es.onmessage=function(ev){
      const d=JSON.parse(ev.data);
      if(d.step==='heartbeat')return;
      if(d.progress>0){document.getElementById('progressFill').style.width=d.progress+'%'}
      document.getElementById('progressText').textContent=d.message;
      if(d.step&&d.step!=='init'&&d.step!=='complete'&&d.step!=='error'&&STEP_LABELS[d.step]){
        completedSteps.add(d.step);
        let html='';
        for(const[k,label]of Object.entries(STEP_LABELS)){
          const cls=completedSteps.has(k)?(d.step===k?'active':'done'):'';
          html+=`<span class="step-tag ${cls}">${label}</span>`;
        }
        document.getElementById('progressSteps').innerHTML=html;
      }
      if(d.step==='complete'){
        es.close();
        document.getElementById('progressFill').style.width='100%';
        showResults(task_id,d.outputs||{});
        btn.disabled=false;btn.textContent='开始处理';
        loadRemaining();loadHistory();
      }else if(d.step==='error'){
        es.close();
        errEl.textContent='处理出错: '+d.message;errEl.style.display='block';
        progArea.style.display='none';
        btn.disabled=false;btn.textContent='开始处理';
        loadHistory();
      }
    };
    es.onerror=function(){
      es.close();
      setTimeout(()=>{pollFallback(task_id,btn,errEl,progArea)},2000);
    };
  }catch(e){errEl.textContent=e.message;errEl.style.display='block';progArea.style.display='none';btn.disabled=false;btn.textContent='开始处理'}
}

async function pollFallback(taskId,btn,errEl,progArea){
  const iv=setInterval(async()=>{
    try{const r=await fetch('/api/status/'+taskId);const d=await r.json();
      document.getElementById('progressText').textContent=d.progress||'处理中...';
      if(d.status==='completed'){clearInterval(iv);document.getElementById('progressFill').style.width='100%';showResults(taskId,d.outputs);btn.disabled=false;btn.textContent='开始处理';loadRemaining();loadHistory()}
      else if(d.status==='error'){clearInterval(iv);errEl.textContent='处理出错: '+(d.error||'未知错误');errEl.style.display='block';progArea.style.display='none';btn.disabled=false;btn.textContent='开始处理';loadHistory()}
    }catch(e){console.error(e)}
  },3000);
}

function showResults(taskId,outputs){
  const area=document.getElementById('resultArea'),files=document.getElementById('resultFiles');
  area.style.display='block';
  let html='';
  for(const[key,fname]of Object.entries(outputs)){html+=`<div class="result-file"><span class="name">${OUTPUT_LABELS[key]||key} — ${fname}</span><a class="dl-btn" href="/api/download/${taskId}/${fname}" download>下载</a></div>`}
  html+=`<a class="dl-all-btn" href="/api/download/${taskId}" download>下载全部 (ZIP)</a>`;
  files.innerHTML=html;
}

async function loadRemaining(){try{const r=await fetch('/api/remaining');const d=await r.json();document.getElementById('remaining').textContent=d.remaining}catch(e){}}
async function loadHistory(){try{const r=await fetch('/api/history');const d=await r.json();const el=document.getElementById('historyList');if(!d.records||!d.records.length){el.innerHTML='<p style="color:var(--text-light);text-align:center;padding:20px">暂无历史记录</p>';return}
  el.innerHTML=d.records.map(rec=>{const sc='status-'+rec.status;const st={processing:'处理中',completed:'已完成',error:'出错'}[rec.status]||rec.status;let a='';if(rec.status==='completed')a=`<div class="history-actions"><a href="/api/download/${rec.task_id}">下载</a></div>`;return`<div class="history-item"><div class="history-info"><div class="title">${rec.input_info}</div><div class="meta">PDF上传 · ${rec.created_at}</div></div><span class="status-badge ${sc}">${st}</span>${a}</div>`}).join('')}catch(e){}}
loadRemaining();loadHistory();
</script>
</body>
</html>'''
