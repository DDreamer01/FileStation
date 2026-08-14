#!/usr/bin/env python3
"""FileStation v3.0 — Enhanced single-file Python web file manager."""

import argparse, base64, hashlib, json, mimetypes, os, secrets
import shutil, ssl, subprocess, tempfile, threading, time, urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "3.1"
CHUNK   = 1 << 18
BLD     = "\033[1m"
RST     = "\033[0m"
MAX_CONN = 48
THUMB_QUALITY = 3
THUMB_HEIGHT = 480
THUMB_DIR = os.path.join(os.path.expanduser("~"), ".filestation_thumbs")

MIME_MAP = {
    ".mp4":"video/mp4",".m4v":"video/mp4",".mov":"video/quicktime",
    ".webm":"video/webm",".mkv":"video/x-matroska",".avi":"video/x-msvideo",
    ".wmv":"video/x-ms-wmv",".flv":"video/x-flv",".ts":"video/mp2t",
    ".m2ts":"video/mp2t",".mts":"video/mp2t",".mpeg":"video/mpeg",
    ".mpg":"video/mpeg",".3gp":"video/3gpp",".3g2":"video/3gpp2",
    ".ogv":"video/ogg",".mp3":"audio/mpeg",".m4a":"audio/mp4",
    ".aac":"audio/aac",".ogg":"audio/ogg",".oga":"audio/ogg",
    ".opus":"audio/opus",".flac":"audio/flac",".wav":"audio/wav",
    ".weba":"audio/webm",".jpg":"image/jpeg",".jpeg":"image/jpeg",
    ".png":"image/png",".gif":"image/gif",".webp":"image/webp",
    ".svg":"image/svg+xml",".ico":"image/x-icon",".bmp":"image/bmp",
    ".tiff":"image/tiff",".tif":"image/tiff",".avif":"image/avif",
    ".txt":"text/plain",".md":"text/markdown",".csv":"text/csv",
    ".html":"text/html",".htm":"text/html",".css":"text/css",
    ".js":"text/javascript",".json":"application/json",
    ".xml":"application/xml",".yaml":"text/yaml",".yml":"text/yaml",
    ".py":"text/x-python",".sh":"text/x-sh",".toml":"application/toml",
    ".ini":"text/plain",".conf":"text/plain",".log":"text/plain",
    ".zip":"application/zip",".tar":"application/x-tar",
    ".gz":"application/gzip",".bz2":"application/x-bzip2",
    ".xz":"application/x-xz",".7z":"application/x-7z-compressed",
    ".rar":"application/vnd.rar",".pdf":"application/pdf",
}

def mime_type(path):
    ext = os.path.splitext(path)[1].lower()
    return MIME_MAP.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"

def human_size(n):
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def safe_path(base, rel):
    base = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base, rel.lstrip("/")))
    return target if (target == base or target.startswith(base + os.sep)) else None

def disk_info(path):
    try:
        s = shutil.disk_usage(path)
        return {"total":s.total,"used":s.used,"free":s.free,
                "pct":round(s.used/s.total*100,1) if s.total else 0}
    except OSError:
        return {"total":0,"used":0,"free":0,"pct":0}

_sessions: dict = {}
_sess_lock = threading.Lock()

def create_session(username):
    token = secrets.token_urlsafe(32)
    with _sess_lock:
        _sessions[token] = {"user":username,"created":time.time()}
    return token

def validate_session(token):
    with _sess_lock:
        s = _sessions.get(token)
        if s and time.time()-s["created"] < 86400:
            return True
        if s:
            del _sessions[token]
    return False

def destroy_session(token):
    with _sess_lock:
        _sessions.pop(token, None)

_zip_keys: dict = {}

def cleanup_old():
    now = time.time()
    for k in list(_zip_keys):
        if now - _zip_keys[k]["created"] > 300:
            del _zip_keys[k]


LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FileStation — Login</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#09090b;--surface:#18181b;--border:#3f3f46;--text:#fafafa;--text2:#a1a1aa;--accent:#8b5cf6;--accent-hover:#7c3aed;--error:#ef4444;--radius:8px}
html{font-family:'Inter',system-ui,sans-serif;font-size:14px;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased;height:100%}body{height:100%;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;background:var(--bg);overflow-x:hidden}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:40px;width:100%;max-width:380px;box-shadow:0 25px 50px rgba(0,0,0,.5)}
h1{font-size:22px;font-weight:700;margin-bottom:8px}
.sub{color:var(--text2);font-size:13px;margin-bottom:28px}
label{display:block;font-size:13px;font-weight:500;margin-bottom:6px;color:var(--text2)}
input{width:100%;padding:10px 12px;background:#27272a;border:1px solid var(--border);border-radius:var(--radius);color:var(--text);font-size:14px;font-family:inherit;outline:none;transition:border-color .15s}
input:focus{border-color:var(--accent)}
.field{margin-bottom:16px}
.btn{width:100%;padding:11px;background:var(--accent);color:#fff;border:none;border-radius:var(--radius);font-size:14px;font-weight:600;font-family:inherit;cursor:pointer;transition:background .15s;margin-top:8px}
.btn:hover{background:var(--accent-hover)}
.err{color:var(--error);font-size:13px;margin-top:12px;display:none}
</style>
</head>
<body>
<div class="card">
  <h1>&#128194; FileStation</h1>
  <p class="sub">Sign in to access your files</p>
  <div class="field"><label>Username</label><input id="u" type="text" autocomplete="username" autofocus></div>
  <div class="field"><label>Password</label><input id="p" type="password" autocomplete="current-password"></div>
  <button class="btn" id="btn">Sign in</button>
  <div class="err" id="err"></div>
</div>
<script>
async function login(){
  const u=document.getElementById('u').value,p=document.getElementById('p').value;
  const r=await fetch('/_api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const d=await r.json();
  if(d.ok){const nx=new URLSearchParams(location.search).get('next')||'/';location.href=nx;}
  else{const e=document.getElementById('err');e.textContent=d.error||'Invalid credentials';e.style.display='block';}
}
document.getElementById('btn').addEventListener('click',login);
document.addEventListener('keydown',e=>{if(e.key==='Enter')login();});
</script>
</body>
</html>"""


UI_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FileStation</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128194;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">




<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#09090b;--surface:#18181b;--surface2:#27272a;--border:#3f3f46;
  --text:#fafafa;--text2:#a1a1aa;--accent:#8b5cf6;--accent-hover:#7c3aed;
  --success:#22c55e;--error:#ef4444;--warn:#eab308;
  --radius:8px;--radius-lg:12px;
}
.markdown-body h1,.markdown-body h2,.markdown-body h3{margin-top:24px;margin-bottom:16px;font-weight:600;line-height:1.25}
.markdown-body h1{font-size:2em;border-bottom:1px solid var(--border);padding-bottom:.3em}
.markdown-body h2{font-size:1.5em;border-bottom:1px solid var(--border);padding-bottom:.3em}
.markdown-body p,.markdown-body blockquote,.markdown-body ul,.markdown-body ol{margin-top:0;margin-bottom:16px}
.markdown-body a{color:var(--accent)}
.markdown-body code{background:rgba(240,246,252,0.15);padding:.2em .4em;border-radius:6px;font-family:monospace;font-size:85%}
.markdown-body pre{background:#161b22;padding:16px;border-radius:6px;overflow:auto}
.markdown-body pre code{background:transparent;padding:0}
.markdown-body blockquote{padding:0 1em;color:var(--text2);border-left:.25em solid var(--border)}
.markdown-body img{max-width:100%;box-sizing:content-box;background-color:var(--bg)}
html{font-family:'Inter',system-ui,sans-serif;font-size:14px;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased;height:100%}
body{height:100vh;overflow:hidden;display:flex;flex-direction:column}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#52525b}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer;border:none;background:none;color:inherit;font-size:inherit}
input,textarea{font-family:inherit;font-size:inherit}
.header{position:sticky;top:0;z-index:100;background:rgba(24,24,27,0.85);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--border);padding:12px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:18px;flex-shrink:0;white-space:nowrap}
.breadcrumbs{display:flex;align-items:center;gap:4px;flex:1;min-width:0;overflow-x:auto;white-space:nowrap;scrollbar-width:none}
.breadcrumbs::-webkit-scrollbar{display:none}
.crumb{color:var(--text2);padding:4px 6px;border-radius:4px;transition:all .15s;font-size:13px;cursor:pointer}
.crumb:hover{color:var(--text);background:var(--surface2)}
.crumb-sep{color:var(--border);font-size:12px;user-select:none}
.crumb:last-child{color:var(--text);font-weight:500}
.search-box{position:relative;flex-shrink:0;width:240px}
.search-box input{width:100%;padding:8px 12px 8px 34px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text);outline:none;transition:border-color .15s}
.search-box input:focus{border-color:var(--accent)}
.search-box input::placeholder{color:var(--text2)}
.search-box svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--text2);pointer-events:none}
.disk-usage{display:flex;align-items:center;gap:8px;flex-shrink:0;font-size:12px;color:var(--text2)}
.disk-bar{width:80px;height:6px;background:var(--surface2);border-radius:3px;overflow:hidden}
.disk-fill{height:100%;background:var(--accent);border-radius:3px;transition:width .3s}
.disk-fill.warn{background:var(--warn)}.disk-fill.danger{background:var(--error)}
.toolbar{display:flex;align-items:center;gap:8px;padding:8px 24px;border-bottom:1px solid var(--border);background:var(--surface);flex-wrap:wrap}
.toolbar-left{display:flex;align-items:center;gap:8px;flex:1}
.toolbar-right{display:flex;align-items:center;gap:8px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:var(--radius);font-size:13px;font-weight:500;transition:all .15s;white-space:nowrap}
.btn-primary{background:var(--accent);color:#fff}.btn-primary:hover{background:var(--accent-hover)}
.btn-danger{background:var(--error);color:#fff}.btn-danger:hover{background:#dc2626}
.btn-ghost{color:var(--text2);background:transparent}.btn-ghost:hover{background:var(--surface2);color:var(--text)}
.btn-outline{border:1px solid var(--border);color:var(--text2)}.btn-outline:hover{border-color:var(--text2);color:var(--text)}
.btn svg{width:16px;height:16px}
.bulk-actions{display:none;align-items:center;gap:8px}.bulk-actions.active{display:flex}

.filter-bar{display:flex;gap:6px;align-items:center;margin-right:12px}
.filter-btn{padding:5px 10px;border-radius:20px;font-size:12px;font-weight:500;background:var(--surface2);color:var(--text2);border:1px solid transparent;cursor:pointer;transition:all .15s}
.filter-btn:hover{color:var(--text);background:var(--surface)}
.filter-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.nav-media-btn{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:44px;border-radius:50%;background:rgba(0,0,0,.6);color:#fff;border:1px solid rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:100;backdrop-filter:blur(4px);transition:all .15s}
.nav-media-btn:hover{background:var(--accent);border-color:var(--accent);transform:translateY(-50%) scale(1.1)}
.nav-media-prev{left:16px}
.nav-media-next{right:16px}

.view-toggle{display:flex;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
.view-btn{padding:6px 10px;color:var(--text2);background:transparent;border:none;cursor:pointer;transition:all .15s;display:flex;align-items:center}
.view-btn.active{background:var(--surface2);color:var(--text)}.view-btn svg{width:16px;height:16px}
.main{display:flex;flex:1;overflow:hidden}
.sidebar{width:220px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);padding:12px 0;overflow-y:auto;display:flex;flex-direction:column;gap:2px}
.sidebar-item{display:flex;align-items:center;gap:8px;padding:8px 16px;color:var(--text2);border-radius:var(--radius);margin:0 8px;cursor:pointer;font-size:13px;transition:all .15s;user-select:none}
.sidebar-item:hover{background:var(--surface2);color:var(--text)}.sidebar-item svg{width:16px;height:16px;flex-shrink:0}
.sidebar-sep{height:1px;background:var(--border);margin:8px 16px}
.content{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}
.drop-zone{border:2px dashed var(--border);border-radius:var(--radius-lg);padding:32px;text-align:center;color:var(--text2);transition:all .2s;cursor:pointer}
.drop-zone:hover,.drop-zone.drag-over{border-color:var(--accent);background:rgba(139,92,246,.05);color:var(--accent)}
.drop-zone svg{width:40px;height:40px;margin:0 auto 12px;display:block;opacity:.6}
.drop-zone .dz-title{font-weight:600;font-size:16px;margin-bottom:4px}.drop-zone .dz-sub{font-size:13px}
.upload-queue{position:fixed;bottom:24px;right:24px;width:340px;max-height:360px;overflow-y:auto;z-index:1000;display:none;flex-direction:column;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;box-shadow:0 12px 32px rgba(0,0,0,.5)}
.upload-queue.active{display:flex}
.upload-queue-header{display:flex;align-items:center;justify-content:space-between;font-weight:600;font-size:13px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.upload-queue-close{background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:0 4px;line-height:1}
.upload-queue-close:hover{color:var(--text)}
.upload-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px 16px;display:flex;align-items:center;gap:12px}
.upload-item-icon{font-size:20px;flex-shrink:0}
.upload-item-info{flex:1;min-width:0}
.upload-item-name{font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.upload-item-meta{font-size:12px;color:var(--text2);margin-top:2px}
.upload-progress{height:4px;background:var(--surface2);border-radius:2px;margin-top:8px;overflow:hidden}
.upload-progress-bar{height:100%;background:var(--accent);border-radius:2px;transition:width .2s;width:0}
.upload-progress-bar.success{background:var(--success)}.upload-progress-bar.error{background:var(--error)}
.upload-status{font-size:12px;color:var(--text2);white-space:nowrap;flex-shrink:0}
.file-table{width:100%;border-collapse:collapse}
.file-table th{text-align:left;padding:8px 12px;color:var(--text2);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border);white-space:nowrap}
.file-table th.sortable{cursor:pointer;user-select:none}.file-table th.sortable:hover{color:var(--text)}
.file-row{border-bottom:1px solid rgba(63,63,70,.4);transition:background .1s;cursor:pointer}
.file-row:hover{background:var(--surface2)}.file-row.selected{background:rgba(139,92,246,.15)}
.file-row td{padding:10px 12px;vertical-align:middle}.file-row td:first-child{width:36px}
.file-check{width:16px;height:16px;accent-color:var(--accent);cursor:pointer}
.file-icon{font-size:20px;margin-right:8px}
.file-name-cell{display:flex;align-items:center}
.file-name{font-weight:500;color:var(--text);font-size:13px}.file-name:hover{color:var(--accent)}
.file-size{color:var(--text2);font-size:13px;white-space:nowrap}
.file-date{color:var(--text2);font-size:12px;white-space:nowrap}
.file-actions{display:flex;gap:4px;opacity:0;transition:opacity .15s}.file-row:hover .file-actions{opacity:1}
.file-action-btn{padding:4px 8px;border-radius:4px;font-size:12px;color:var(--text2);background:var(--surface2);transition:all .1s}
.file-action-btn:hover{color:var(--text);background:var(--border)}
.file-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px}
.grid-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;cursor:pointer;transition:all .2s;position:relative}
.grid-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.4)}
.grid-card.selected{border-color:var(--accent);background:rgba(139,92,246,.1)}
.grid-card-thumb{width:100%;aspect-ratio:16/10;background:var(--surface2);display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.grid-card-thumb img,.grid-card-thumb video{width:100%;height:100%;object-fit:cover}
.grid-card-thumb .thumb-icon{font-size:48px;opacity:.7}
.video-badge{position:absolute;bottom:6px;right:6px;background:rgba(0,0,0,.7);color:#fff;font-size:10px;padding:2px 6px;border-radius:4px;backdrop-filter:blur(4px)}
.play-overlay{position:absolute;inset:0;background:rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .2s}
.grid-card:hover .play-overlay{opacity:1}.play-overlay svg{width:40px;height:40px;color:#fff;filter:drop-shadow(0 2px 8px rgba(0,0,0,.5))}
.grid-card-info{padding:10px 12px}
.grid-card-name{font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text)}
.grid-card-meta{font-size:11px;color:var(--text2);margin-top:2px}
.grid-card-check{position:absolute;top:8px;left:8px;width:20px;height:20px;accent-color:var(--accent);cursor:pointer;opacity:1;z-index:5;transition:opacity .15s}
.grid-card-actions{position:absolute;top:8px;right:8px;display:flex;gap:4px;opacity:0;transition:opacity .15s}
.grid-card:hover .grid-card-actions{opacity:1}
.grid-action-btn{width:26px;height:26px;border-radius:4px;background:rgba(0,0,0,.6);color:#fff;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);transition:background .15s}
.grid-action-btn:hover{background:var(--accent)}.grid-action-btn svg{width:13px;height:13px}
.folder-card-thumb{background:linear-gradient(135deg,#1e1e24 0%,#27272a 100%)}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 24px;color:var(--text2);text-align:center;gap:12px}
.empty svg{width:56px;height:56px;opacity:.4}.empty-title{font-size:18px;font-weight:600;color:var(--text)}.empty-sub{font-size:14px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .2s;backdrop-filter:blur(4px)}
.modal-overlay.active{opacity:1;pointer-events:all}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:28px;width:100%;max-width:500px;box-shadow:0 25px 50px rgba(0,0,0,.6);transform:translateY(8px);transition:transform .2s}
.modal-overlay.active .modal{transform:translateY(0)}
.modal-lg{max-width:860px}
.modal-xl{max-width:96vw;height:90vh;display:flex;flex-direction:column;padding:28px}
.modal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.modal-title{font-size:16px;font-weight:600}
.modal-close{width:28px;height:28px;display:flex;align-items:center;justify-content:center;border-radius:6px;color:var(--text2);background:var(--surface2);transition:all .15s;flex-shrink:0;cursor:pointer}
.modal-close:hover{color:var(--text);background:var(--border)}
.modal-footer{display:flex;gap:10px;justify-content:flex-end;margin-top:20px}
.field{margin-bottom:16px}
.field label{display:block;font-size:13px;font-weight:500;margin-bottom:6px;color:var(--text2)}
.field input,.field select,.field textarea{width:100%;padding:9px 12px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);color:var(--text);outline:none;transition:border-color .15s}
.field input:focus,.field select:focus,.field textarea:focus{border-color:var(--accent)}
.video-modal-body{flex:1;display:flex;flex-direction:column;overflow:hidden;gap:12px;min-height:0}
.video-wrap{flex:1;background:#000;border-radius:var(--radius);overflow:hidden;display:flex;align-items:center;justify-content:center;min-height:0}
.video-wrap video{max-width:100%;max-height:100%;outline:none}
.video-info{font-size:13px;color:var(--text2)}
.image-modal-body{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000;border-radius:var(--radius)}
.image-modal-body img{max-width:100%;max-height:100%;object-fit:contain}
.preview-body{flex:1;display:flex;flex-direction:column;overflow:auto;background:#0d1117;border:1px solid var(--border);border-radius:var(--radius);min-height:0}
.preview-body iframe{width:100%;height:100%;border:none;background:#fff;flex:1}
.preview-body pre{background:transparent;margin:0;padding:16px;white-space:pre-wrap;word-break:break-word;color:#e6edf3;font-family:'Cascadia Code','Fira Code',monospace;font-size:13px;line-height:1.6;flex:1}
.preview-body .preview-note{padding:8px 16px;color:var(--text2);font-size:12px;border-top:1px solid var(--border)}
.editor-body{flex:1;display:flex;flex-direction:column;overflow:hidden;gap:0;min-height:0}
.editor-toolbar{display:flex;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);margin-bottom:8px;flex-wrap:wrap;align-items:center}
.editor-textarea{flex:1;background:#0d1117;color:#e6edf3;border:1px solid var(--border);border-radius:var(--radius);padding:16px;font-family:'Cascadia Code','Fira Code',monospace;font-size:13px;line-height:1.6;resize:none;outline:none;overflow-y:auto;tab-size:2;min-height:0}
.editor-textarea:focus{border-color:var(--accent)}
.editor-status{font-size:12px;color:var(--text2);display:flex;gap:16px}
.folder-tree{max-height:320px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface2)}
.tree-item{display:flex;align-items:center;gap:8px;padding:8px 12px;cursor:pointer;font-size:13px;color:var(--text2);transition:all .15s;user-select:none}
.tree-item:hover{background:var(--border);color:var(--text)}.tree-item.active{background:rgba(139,92,246,.2);color:var(--accent)}
.tree-item svg{width:16px;height:16px;flex-shrink:0}
.tree-chevron{width:14px;height:14px;display:inline-flex;align-items:center;justify-content:center;font-size:10px;color:var(--text2);flex-shrink:0;visibility:hidden}
.tree-chevron.expandable{visibility:visible;cursor:pointer}
.tree-chevron.open{transform:rotate(90deg)}
.tree-loading{pointer-events:none}
.notif-container{position:fixed;bottom:24px;right:24px;z-index:2000;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.notif{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px 16px;font-size:13px;box-shadow:0 8px 24px rgba(0,0,0,.4);pointer-events:all;display:flex;align-items:center;gap:10px;max-width:320px;animation:notifIn .25s ease;transition:opacity .3s,transform .3s}
.notif.hide{opacity:0;transform:translateX(20px)}
.notif.success{border-left:3px solid var(--success)}.notif.error{border-left:3px solid var(--error)}.notif.info{border-left:3px solid var(--accent)}
@keyframes notifIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
.file-row.drop-target{background:rgba(139,92,246,.15);outline:2px solid var(--accent)}
.grid-card.drop-target{border-color:var(--accent);background:rgba(139,92,246,.2)}
/* Bottom Sheet for Mobile Actions */
.bottom-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 1100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.bottom-sheet-overlay.active {
  opacity: 1;
  pointer-events: all;
}
.bottom-sheet {
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-radius: 16px 16px 0 0;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 -8px 32px rgba(0,0,0,0.5);
  transform: translateY(100%);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 16px 16px 24px;
}
.bottom-sheet-overlay.active .bottom-sheet {
  transform: translateY(0);
}
.bottom-sheet-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
  gap: 8px;
}
.bottom-sheet-drag-handle {
  width: 36px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
}
.bottom-sheet-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bottom-sheet-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bottom-sheet-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
  background: transparent;
  border: none;
  transition: background 0.15s;
  text-align: left;
}
.bottom-sheet-item:hover {
  background: var(--surface2);
}
.bottom-sheet-item svg {
  width: 18px;
  height: 18px;
  color: var(--text2);
}
.bottom-sheet-item.danger {
  color: var(--error);
}
.bottom-sheet-item.danger svg {
  color: var(--error);
}

.mobile-only-svg {
  display: none !important;
}
.mobile-more-btn {
  display: none !important;
}
.desktop-actions {
  display: flex;
  gap: 4px;
}
.hamburger-btn {
  display: none;
}
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 1040;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.sidebar-overlay.active {
  opacity: 1;
  pointer-events: all;
}

@media(max-width:768px){
  .mobile-only-svg {
    display: block !important;
  }
  .mobile-more-btn {
    display: flex !important;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    background: var(--surface2);
    color: var(--text2);
    border: none;
    cursor: pointer;
  }
  .desktop-actions {
    display: none !important;
  }
  .file-actions, .grid-card-actions {
    opacity: 1 !important;
  }
  .hamburger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: var(--radius);
    color: var(--text2);
    cursor: pointer;
    transition: all .15s;
    background: transparent;
    border: none;
    padding: 0;
  }
  .hamburger-btn:hover {
    color: var(--text);
    background: var(--surface2);
  }
  .sidebar{
    display: flex !important;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    z-index: 1050;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: var(--surface);
    border-right: 1px solid var(--border);
    box-shadow: 24px 0 48px rgba(0,0,0,0.8);
    padding: 16px 0;
  }
  .sidebar.active{
    transform: translateX(0);
  }
  .main{flex-direction:column;height:auto}
  .file-name-cell {
    min-width: 0;
    max-width: calc(100vw - 160px);
  }
  .file-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .content{padding:16px;gap:12px}
  .header{padding:10px 12px;gap:8px 12px}
  .logo{font-size:16px}
  .logo svg{width:24px;height:24px}
  .breadcrumbs{order:3;flex-basis:100%;min-width:0}
  .search-box{order:4;width:100%;flex-basis:100%;margin-top:2px}
  .disk-usage{
    display: flex;
    order: 2;
    margin-left: auto;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text2);
  }
  .disk-text{
    display: none;
  }
  .disk-bar{
    width: 60px;
    height: 5px;
  }
  .logout-text {
    display: none;
  }
  #btn-logout {
    padding: 8px;
  }
  .toolbar{
    flex-direction: column;
    align-items: stretch;
    padding: 8px 12px;
    gap: 8px;
  }
  .toolbar-left {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }
  .toolbar-right {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 8px;
  }
  .filter-bar {
    flex: 1;
    overflow-x: auto;
    max-width: calc(100% - 80px);
    margin-right: 0;
    flex-wrap: nowrap;
    padding-bottom: 2px;
  }
  .file-table .file-date{display:none}
  .file-grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px}
  .file-table th,.file-table td{padding:8px 10px}
  .grid-card-check{width:22px;height:22px}
  .grid-action-btn{width:30px;height:30px}
  .upload-queue{left:16px;right:16px;width:auto;bottom:16px}
  .modal-xl{max-width:100vw;height:96vh;padding:16px}
  .modal{padding:20px}
  .drop-zone{padding:20px}
  
  .bulk-actions.active {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 12px 24px;
    z-index: 999;
    display: flex;
    justify-content: space-around;
    align-items: center;
    box-shadow: 0 -8px 24px rgba(0,0,0,0.5);
  }
  .bulk-actions.active .btn-text {
    display: none;
  }
  .bulk-actions.active .btn {
    padding: 10px;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
</head>
<body>
<div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSidebar()"></div>
<header class="header">
  <button class="hamburger-btn" id="hamburger-btn" onclick="toggleSidebar()" aria-label="Toggle menu">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
  </button>
  <div class="logo">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:28px;height:28px;color:var(--accent)"><path d="M3 7a2 2 0 012-2h3.586a1 1 0 01.707.293L11 7h10a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg>
    FileStation
  </div>
  <nav class="breadcrumbs" id="breadcrumbs"></nav>
  <div class="search-box">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="text" id="search" placeholder="Search files...">
  </div>
  <div class="disk-usage" id="disk-usage">
    <span id="disk-text" class="disk-text">-</span>
    <div class="disk-bar"><div class="disk-fill" id="disk-fill" style="width:0%"></div></div>
  </div>
  <button class="btn btn-ghost" id="btn-logout" style="display:none">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
    <span class="btn-text">Logout</span>
  </button>
</header>
<div class="toolbar">
  <div class="toolbar-left">
    <div class="bulk-actions" id="bulk-actions">
      <span id="sel-count" style="font-size:13px;color:var(--text2)"></span>
      <button class="btn btn-outline" id="btn-download-sel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <span class="btn-text">Download</span>
      </button>
      <button class="btn btn-outline" id="btn-copy-sel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
        <span class="btn-text">Copy Links</span>
      </button>
      <button class="btn btn-outline" id="btn-move-sel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><polyline points="5 9 2 12 5 15"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/></svg>
        <span class="btn-text">Move</span>
      </button>
      <button class="btn btn-danger" id="btn-delete-sel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
        <span class="btn-text">Delete</span>
      </button>
      <button class="btn btn-ghost" id="btn-deselect">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mobile-only-svg" style="width:18px;height:18px"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        <span class="btn-text">Clear</span>
      </button>
    </div>
    <button class="btn btn-primary" id="btn-upload" style="display:none">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      Upload
    </button>
    <button class="btn btn-outline" id="btn-mkdir" style="display:none">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
      New folder
    </button>
    <button class="btn btn-outline" id="btn-newfile" style="display:none">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
      New file
    </button>
  </div>
  <div class="toolbar-right">
    <div class="filter-bar" id="filter-bar">
      <button class="filter-btn active" data-cat="all" onclick="setCategoryFilter('all')">All</button>
      <button class="filter-btn" data-cat="video" onclick="setCategoryFilter('video')">🎬 Videos</button>
      <button class="filter-btn" data-cat="image" onclick="setCategoryFilter('image')">🖼️ Images</button>
      <button class="filter-btn" data-cat="audio" onclick="setCategoryFilter('audio')">🎵 Audio</button>
      <button class="filter-btn" data-cat="doc" onclick="setCategoryFilter('doc')">📄 Docs</button>
    </div>
    <div class="view-toggle">
      <button class="view-btn active" id="view-list" title="List view">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
      </button>
      <button class="view-btn" id="view-grid" title="Grid view">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
      </button>
    </div>
  </div>
</div>
<div class="main">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-item" onclick="navigate('/')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      Home
    </div>
    <div class="sidebar-sep"></div>
    <div class="sidebar-item" style="color:var(--text2);cursor:default">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      Recent
    </div>
    <div id="recent-list" style="display:flex;flex-direction:column;gap:2px"></div>
    <div style="flex:1"></div>
    <div class="sidebar-disk" style="padding:16px;margin:8px;border-top:1px solid var(--border)">
      <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text2);margin-bottom:6px">
        <span>Storage</span>
        <span id="sidebar-disk-text">-</span>
      </div>
      <div class="disk-bar" style="width:100%;height:6px;background:var(--surface2);border-radius:3px;overflow:hidden">
        <div class="disk-fill" id="sidebar-disk-fill" style="width:0%"></div>
      </div>
    </div>
  </aside>
  <main class="content" id="content">
    <div class="drop-zone" id="drop-zone" style="display:none">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      <div class="dz-title">Drop files to upload</div>
      <div class="dz-sub">or click to browse - multiple files supported</div>
    </div>
    <div class="upload-queue" id="upload-queue">
    <div class="upload-queue-header">
      <span id="upload-queue-title">Uploading...</span>
      <button class="upload-queue-close" onclick="closeUploadQueue()">×</button>
    </div>
    <div id="upload-queue-items" style="display:flex;flex-direction:column;gap:8px"></div>
  </div>
    <div id="file-listing"></div>
  </main>
</div>
<input type="file" id="file-input" multiple style="display:none">
<div class="notif-container" id="notif-container"></div>

<!-- Mkdir -->
<div class="modal-overlay" id="modal-mkdir">
  <div class="modal">
    <div class="modal-header"><span class="modal-title">New folder</span><button class="modal-close" onclick="closeModal('modal-mkdir')">x</button></div>
    <div class="field"><label>Folder name</label><input id="mkdir-name" type="text" placeholder="folder-name"></div>
    <div class="modal-footer"><button class="btn btn-ghost" onclick="closeModal('modal-mkdir')">Cancel</button><button class="btn btn-primary" id="mkdir-submit">Create</button></div>
  </div>
</div>

<!-- Editor -->
<div class="modal-overlay" id="modal-editor">
  <div class="modal modal-xl">
    <div class="modal-header"><span class="modal-title" id="editor-title">New file</span><button class="modal-close" onclick="closeModal('modal-editor')">x</button></div>
    <div class="editor-body">
      <div class="editor-toolbar">
        <button class="btn btn-ghost" style="font-size:12px" onclick="editorIndent()">Tab Indent</button>
        <button class="btn btn-ghost" style="font-size:12px" onclick="editorWrap('`','`')">Code</button>
        <button class="btn btn-ghost" style="font-size:12px" onclick="editorWrap('**','**')">Bold</button>
        <button class="btn btn-ghost" style="font-size:12px" onclick="editorWrap('_','_')">Italic</button>
        <div style="flex:1"></div>
        <div class="editor-status"><span id="editor-lines">0 lines</span><span id="editor-chars">0 chars</span></div>
      </div>
      <textarea class="editor-textarea" id="editor-textarea" spellcheck="false"></textarea>
    </div>
    <div class="modal-footer" style="padding-top:12px">
      <div class="field" style="margin:0;flex:1"><input id="editor-filename" type="text" placeholder="filename.txt"></div>
      <button class="btn btn-ghost" onclick="closeModal('modal-editor')">Cancel</button>
      <button class="btn btn-primary" id="editor-save">Save</button>
    </div>
  </div>
</div>

<!-- Rename -->
<div class="modal-overlay" id="modal-rename">
  <div class="modal">
    <div class="modal-header"><span class="modal-title">Rename</span><button class="modal-close" onclick="closeModal('modal-rename')">x</button></div>
    <div class="field"><label>New name</label><input id="rename-val" type="text"></div>
    <div class="modal-footer"><button class="btn btn-ghost" onclick="closeModal('modal-rename')">Cancel</button><button class="btn btn-primary" id="rename-submit">Rename</button></div>
  </div>
</div>

<!-- Move -->
<div class="modal-overlay" id="modal-move">
  <div class="modal modal-lg">
    <div class="modal-header"><span class="modal-title">Move to folder</span><button class="modal-close" onclick="closeModal('modal-move')">x</button></div>
    <p style="font-size:13px;color:var(--text2);margin-bottom:12px">Select destination folder:</p>
    <div class="folder-tree" id="move-tree"></div>
    <div class="modal-footer"><button class="btn btn-ghost" onclick="closeModal('modal-move')">Cancel</button><button class="btn btn-primary" id="move-submit">Move here</button></div>
  </div>
</div>

<!-- Video -->
<div class="modal-overlay" id="modal-video">
  <button class="nav-media-btn nav-media-prev" onclick="navigateMedia(-1)">&lt;</button>
  <button class="nav-media-btn nav-media-next" onclick="navigateMedia(1)">&gt;</button>
  <div class="modal modal-xl">
    <div class="modal-header"><span class="modal-title" id="video-title">Video</span><div style="display:flex;align-items:center;gap:8px;"><button class="btn btn-outline btn-sm" id="video-copy-link" style="padding:4px 10px;font-size:12px;display:flex;align-items:center;gap:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg><span>Copy Link</span></button><button class="modal-close" onclick="closeVideo()">x</button></div></div>
    <div class="video-modal-body">
      <div class="video-wrap"><video id="video-player" controls preload="metadata" playsinline>Your browser does not support HTML5 video.</video></div>
      <div class="video-info" id="video-info"></div>
    </div>
  </div>
</div>

<!-- Image -->
<div class="modal-overlay" id="modal-image">
  <button class="nav-media-btn nav-media-prev" onclick="navigateMedia(-1)">&lt;</button>
  <button class="nav-media-btn nav-media-next" onclick="navigateMedia(1)">&gt;</button>
  <div class="modal modal-xl">
    <div class="modal-header"><span class="modal-title" id="image-title">Image</span><div style="display:flex;align-items:center;gap:8px;"><button class="btn btn-outline btn-sm" id="image-copy-link" style="padding:4px 10px;font-size:12px;display:flex;align-items:center;gap:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg><span>Copy Link</span></button><button class="modal-close" onclick="closeModal('modal-image')">x</button></div></div>
    <div class="image-modal-body"><img id="image-viewer" src="" alt=""></div>
  </div>
</div>

<!-- Preview -->
<div class="modal-overlay" id="modal-preview">
  <div class="modal modal-xl">
    <div class="modal-header"><span class="modal-title" id="preview-title">Preview</span><button class="modal-close" onclick="closeModal('modal-preview')">x</button></div>
    <div class="preview-body" id="preview-body"></div>
    <div class="modal-footer"><button class="btn btn-primary" id="preview-edit" style="display:none">Edit</button><button class="btn btn-outline" id="preview-copy-link">Copy Link</button><button class="btn btn-outline" id="preview-download">Download</button><button class="btn btn-ghost" onclick="closeModal('modal-preview')">Close</button></div>
  </div>
</div>

<!-- Mobile Actions Bottom Sheet -->
<div class="bottom-sheet-overlay" id="sheet-actions" onclick="closeSheet('sheet-actions')">
  <div class="bottom-sheet" onclick="event.stopPropagation()">
    <div class="bottom-sheet-header">
      <div class="bottom-sheet-drag-handle"></div>
      <span class="bottom-sheet-title" id="sheet-title">File Options</span>
    </div>
    <div class="bottom-sheet-content" id="sheet-content">
    </div>
  </div>
</div>

<!-- Delete -->
<div class="modal-overlay" id="modal-delete">
  <div class="modal">
    <div class="modal-header"><span class="modal-title">Confirm delete</span><button class="modal-close" onclick="closeModal('modal-delete')">x</button></div>
    <p id="delete-msg" style="font-size:14px;color:var(--text2);margin-bottom:8px"></p>
    <div class="modal-footer"><button class="btn btn-ghost" onclick="closeModal('modal-delete')">Cancel</button><button class="btn btn-danger" id="delete-confirm">Delete</button></div>
  </div>
</div>

<script>
const IS_ADMIN="__IS_ADMIN__"==="true";
const MAX_UPLOAD=parseInt("__MAX_UPLOAD__")||2*1024*1024*1024;
let currentPath="/",currentEntries=[],selected=new Set(),viewMode=localStorage.getItem("viewMode")||"list";
let sortKey="name",sortAsc=true,searchTimer=null;
let recentPaths=JSON.parse(localStorage.getItem("recentPaths")||"[]").slice(0,8);
let moveTargetPath="/",editorMode="new",editorFilePath=null,pendingDeletePaths=[];
let renameFromPath="",movePaths=[];
const VIDEO_EXTS=new Set([".mp4",".m4v",".webm",".mov",".mkv",".avi",".ogv",".ts",".m2ts",".mts",".flv",".wmv",".mpeg",".mpg",".3gp",".3g2"]);
const AUDIO_EXTS=new Set([".mp3",".m4a",".aac",".ogg",".oga",".opus",".flac",".wav",".weba"]);
const IMAGE_EXTS=new Set([".jpg",".jpeg",".png",".gif",".webp",".svg",".bmp",".ico",".tiff",".tif",".avif"]);
const TEXT_EXTS=new Set([".txt",".md",".csv",".html",".htm",".css",".js",".ts",".json",".xml",".yaml",".yml",".py",".sh",".toml",".ini",".conf",".log",".rs",".go",".java",".c",".cpp",".h",".rb",".php",".swift",".kt",".dart",".vue",".jsx",".tsx",".sql",".env",".gitignore"]);
function ext(n){return(n.lastIndexOf(".")>=0?n.slice(n.lastIndexOf(".")):"").toLowerCase();}
function isVideo(e){return VIDEO_EXTS.has(ext(e.name));}
function isAudio(e){return AUDIO_EXTS.has(ext(e.name));}
function isImage(e){return IMAGE_EXTS.has(ext(e.name));}
function isText(e){return TEXT_EXTS.has(ext(e.name));}
function humanSize(n){if(n===undefined||n===null)return"-";const u=["B","KB","MB","GB","TB"];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++;}return i===0?n+" "+u[i]:n.toFixed(1)+" "+u[i];}
function humanDate(ts){if(!ts)return"-";const d=new Date(ts*1000);return d.toLocaleDateString()+' '+d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});}
function joinPath(...parts){let p=parts.join("/").replace(/\/+/g,"/");if(!p.startsWith("/"))p="/"+p;return p;}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");}
function jesc(s){return JSON.stringify(String(s)).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function encPath(p){return String(p).split("/").map(encodeURIComponent).join("/");}
function copyLink(ev,fp){
  if(ev)ev.stopPropagation();
  let cleanFp=String(fp);if(!cleanFp.startsWith("/"))cleanFp="/"+cleanFp;
  let fullUrl=location.origin+encPath(cleanFp);
  if(navigator.clipboard&&window.isSecureContext){
    navigator.clipboard.writeText(fullUrl).then(()=>{notify("Link copied to clipboard","success");}).catch(()=>fallbackCopy(fullUrl));
  }else{
    fallbackCopy(fullUrl);
  }
}
function fallbackCopy(text){
  try{
    const ta=document.createElement("textarea");
    ta.value=text;ta.style.position="fixed";ta.style.top="0";ta.style.left="0";ta.style.opacity="0";ta.style.pointerEvents="none";
    document.body.appendChild(ta);ta.focus();ta.select();
    const ok=document.execCommand("copy");
    document.body.removeChild(ta);
    if(ok){notify("Link copied to clipboard","success");}
    else{prompt("Copy link:",text);}
  }catch(e){prompt("Copy link:",text);}
}
function notify(msg,type="info",duration=3500){
  const c=document.getElementById("notif-container");const n=document.createElement("div");
  n.className=`notif ${type}`;const icon=type==="success"?"✓":type==="error"?"✕":"i";
  n.innerHTML=`<span style="font-size:16px;flex-shrink:0">${icon}</span><span>${msg}</span>`;
  c.appendChild(n);setTimeout(()=>{n.classList.add("hide");setTimeout(()=>n.remove(),300);},duration);
}
async function api(method,url,body){
  const opts={method,headers:{}};
  if(body!==undefined){opts.body=JSON.stringify(body);opts.headers["Content-Type"]="application/json";}
  const r=await fetch(url,opts);
  if(r.status===401){
    location.href=API_BASE+"_login?next="+encodeURIComponent(location.pathname);
    return {_status:401, error:"Unauthorized"};
  }
  try{return await r.json();}catch{return{_status:r.status, error:"Invalid response"};}
}
async function navigate(path,pushState=true){
  closeSidebar();
  currentPath=path||"/";selected.clear();updateBulkActions();
  if(pushState){
    let rel = currentPath.startsWith("/") ? currentPath.substring(1) : currentPath;
    let targetUrl = currentPath === "/" ? API_BASE : (API_BASE + rel);
    history.pushState({path:currentPath},"",targetUrl);
  }
  await loadDir(currentPath);addRecent(currentPath);
}
function addRecent(path){
  if(path==="/")return;
  recentPaths=recentPaths.filter(p=>p!==path);recentPaths.unshift(path);recentPaths=recentPaths.slice(0,8);
  localStorage.setItem("recentPaths",JSON.stringify(recentPaths));renderRecent();
}
function renderRecent(){
  const el=document.getElementById("recent-list");
  el.innerHTML=recentPaths.map(p=>`<div class="sidebar-item" style="padding-left:28px" onclick="navigate(${jesc(p)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px"><path d="M3 7a2 2 0 012-2h3.586a1 1 0 01.707.293L11 7h10a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(p.split("/").pop()||p)}</span></div>`).join("");
}
async function loadDir(path){
  const data=await api("GET",`${API_BASE}_api/list?path=${encodeURIComponent(path)}`);
  if(data.error){notify(data.error,"error");return;}
  currentEntries=data.entries||[];updateBreadcrumbs(path);updateDisk(data.disk);renderEntries(currentEntries);updateMediaList();
}
function updateBreadcrumbs(path){
  const parts=path.split("/").filter(Boolean);let html=`<span class="crumb" onclick="navigate('/')">~</span>`;let acc="/";
  for(const p of parts){acc=joinPath(acc,p);const a=acc;html+=`<span class="crumb-sep">></span><span class="crumb" onclick="navigate(${jesc(a)})">${esc(p)}</span>`;}
  document.getElementById("breadcrumbs").innerHTML=html;
}
function updateDisk(d){
  if(!d)return;const t=document.getElementById("disk-text");const f=document.getElementById("disk-fill");
  const st=document.getElementById("sidebar-disk-text");const sf=document.getElementById("sidebar-disk-fill");
  const sizeText=`${humanSize(d.used)} / ${humanSize(d.total)}`;const pct=d.pct||0;
  if(t)t.textContent=sizeText;
  if(f){f.style.width=pct+"%";f.className="disk-fill"+(pct>90?" danger":pct>70?" warn":"");}
  if(st)st.textContent=sizeText;
  if(sf){sf.style.width=pct+"%";sf.className="disk-fill"+(pct>90?" danger":pct>70?" warn":"");}
}
function getIcon(e){
  if(e.type==="dir")return"📁";const x=ext(e.name);
  if(VIDEO_EXTS.has(x))return"🎬";if(AUDIO_EXTS.has(x))return"🎵";if(IMAGE_EXTS.has(x))return"🖼️";
  if([".pdf"].includes(x))return"📄";if([".zip",".tar",".gz",".bz2",".xz",".7z",".rar"].includes(x))return"📦";
  if(TEXT_EXTS.has(x))return"📝";return"📄";
}
function sortEntries(entries){
  const dirs=entries.filter(e=>e.type==="dir");const files=entries.filter(e=>e.type!=="dir");
  const cmp=(a,b)=>{let av=a[sortKey]||"",bv=b[sortKey]||"";if(typeof av==="string")av=av.toLowerCase();if(typeof bv==="string")bv=bv.toLowerCase();if(av<bv)return sortAsc?-1:1;if(av>bv)return sortAsc?1:-1;return 0;};
  return[...dirs.sort(cmp),...files.sort(cmp)];
}
function filePath(e){return joinPath(currentPath,e.name);}

let currentCategory = 'all';
let currentMediaList = [];
let currentMediaIndex = -1;

function setCategoryFilter(cat){
  currentCategory = cat;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cat === cat);
  });
  renderEntries(currentEntries);
  updateMediaList();
}

function getCategory(item){
  if(item.type === 'dir') return 'dir';
  const x = (item.name.lastIndexOf('.')>=0 ? item.name.slice(item.name.lastIndexOf('.')) : '').toLowerCase();
  if(VIDEO_EXTS.has(x)) return 'video';
  if(IMAGE_EXTS.has(x)) return 'image';
  if(AUDIO_EXTS.has(x)) return 'audio';
  return 'doc';
}

function filterEntriesByCategory(entries){
  if(currentCategory === 'all') return entries;
  return entries.filter(e => e.type === 'dir' || getCategory(e) === currentCategory);
}

function renderEntries(entries){
  const filtered = filterEntriesByCategory(entries);
  const sorted=sortEntries(filtered);const el=document.getElementById("file-listing");
  if(!sorted.length){el.innerHTML=`<div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 012-2h3.586a1 1 0 01.707.293L11 7h10a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg><div class="empty-title">Empty folder</div><div class="empty-sub">Upload files or create a new folder to get started</div></div>`;return;}
  if(viewMode==="grid")el.innerHTML=renderGrid(sorted);else el.innerHTML=renderList(sorted);
  attachEntryEvents();
}
function renderList(entries){
  const rows=entries.map(e=>{
    const fp=filePath(e);const sel=selected.has(fp);const isDir=e.type==="dir";
    const drag=IS_ADMIN?"draggable='true'":"";
    const hasActions = true;
    return`<tr class="file-row${sel?" selected":""}" data-path="${esc(fp)}" data-type="${e.type}" ${drag}><td><input type="checkbox" class="file-check" ${sel?"checked":""}  onclick="toggleSelect(event,${jesc(fp)})"></td><td><div class="file-name-cell"><span class="file-icon">${getIcon(e)}</span><span class="file-name" title="${esc(e.name)}">${esc(e.name)}</span></div></td><td class="file-size">${isDir?(e.children!==undefined?e.children+" items":"-"):humanSize(e.size)}</td><td class="file-date">${humanDate(e.modified)}</td><td><div class="file-actions"><div class="desktop-actions">${IS_ADMIN&&isText(e)?`<button class="file-action-btn" onclick="editFile(event,${jesc(fp)},${jesc(e.name)})">Edit</button>`:""}${IS_ADMIN?`<button class="file-action-btn" onclick="startRename(event,${jesc(fp)},${jesc(e.name)})">Rename</button>`:""}${IS_ADMIN?`<button class="file-action-btn" onclick="startMoveOne(event,${jesc(fp)})">Move</button>`:""}<button class="file-action-btn" onclick="copyLink(event,${jesc(fp)})">Copy Link</button>${!isDir?`<button class="file-action-btn" onclick="downloadFile(event,${jesc(fp)})">Download</button>`:""}${IS_ADMIN?`<button class="file-action-btn" style="color:var(--error)" onclick="confirmDelete(event,[${jesc(fp)}])">Delete</button>`:""}</div>${hasActions ? `<button class="file-action-btn mobile-more-btn" onclick="openBottomSheet(event,${jesc(fp)},${jesc(e.name)},${isDir},${isText(e)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg></button>` : ""}</div></td></tr>`;
  }).join("");
  return`<table class="file-table"><thead><tr><th><input type="checkbox" class="file-check" id="chk-all" onclick="toggleAll(event)"></th><th class="sortable" onclick="setSort('name')">Name ${sortKey==='name'?(sortAsc?'&uarr;':'&darr;'):''}</th><th class="sortable" onclick="setSort('size')">Size ${sortKey==='size'?(sortAsc?'&uarr;':'&darr;'):''}</th><th class="sortable file-date" onclick="setSort('modified')">Modified ${sortKey==='modified'?(sortAsc?'&uarr;':'&darr;'):''}</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
}
function renderGrid(entries){
  const cards=entries.map(e=>{
    const fp=filePath(e);const sel=selected.has(fp);const isDir=e.type==="dir";const x=ext(e.name);
    const drag=IS_ADMIN?"draggable='true'":"";
    let thumb="";
    if(isDir)thumb=`<div class="grid-card-thumb folder-card-thumb"><span class="thumb-icon">📁</span></div>`;
    else if(IMAGE_EXTS.has(x))thumb=`<div class="grid-card-thumb"><img loading="lazy" src="${encPath(fp)}?preview=1" alt="${esc(e.name)}" onerror="this.style.display='none'"></div>`;
    else if(VIDEO_EXTS.has(x))thumb=`<div class="grid-card-thumb" style="background:#000"><img loading="lazy" src="${encPath(fp)}?thumb=1" alt="${esc(e.name)}" onerror="videoThumbFallback(this)"><div class="video-badge" style="position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,0.7);padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;color:#fff">&#9654;</div></div>`;
    else thumb=`<div class="grid-card-thumb"><span class="thumb-icon">${getIcon(e)}</span></div>`;
    return`<div class="grid-card${sel?" selected":""}" data-path="${esc(fp)}" data-type="${e.type}" ${drag}><input type="checkbox" class="grid-card-check" ${sel?"checked":""} onclick="toggleSelect(event,${jesc(fp)})">${thumb}<div class="grid-card-info"><div class="grid-card-name" title="${esc(e.name)}">${esc(e.name)}</div><div class="grid-card-meta">${isDir?(e.children!==undefined?e.children+" items":"-"):humanSize(e.size)}</div></div><div class="grid-card-actions"><div class="desktop-actions"><button class="grid-action-btn" title="Copy Link" onclick="copyLink(event,${jesc(fp)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button>${!isDir?`<button class="grid-action-btn" title="Download" onclick="downloadFile(event,${jesc(fp)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>`:""}${IS_ADMIN&&isText(e)?`<button class="grid-action-btn" title="Edit" onclick="editFile(event,${jesc(fp)},${jesc(e.name)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>`:""}${IS_ADMIN?`<button class="grid-action-btn" title="Move" onclick="startMoveOne(event,${jesc(fp)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 9 2 12 5 15"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/></svg></button>`:""}${IS_ADMIN?`<button class="grid-action-btn" title="Rename" onclick="startRename(event,${jesc(fp)},${jesc(e.name)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z"/></svg></button>`:""}${IS_ADMIN?`<button class="grid-action-btn" title="Delete" style="color:#f87171" onclick="confirmDelete(event,[${jesc(fp)}])"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg></button>`:""}</div><button class="grid-action-btn mobile-more-btn" onclick="openBottomSheet(event,${jesc(fp)},${jesc(e.name)},${isDir},${isText(e)})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg></button></div></div>`;
  }).join("");
  return`<div class="file-grid">${cards}</div>`;
}
let isInternalDrag = false;

function attachEntryEvents(){
  // Event delegation is used now
}

const fileListing = document.getElementById("file-listing");
fileListing.addEventListener("click", e => {
  const row = e.target.closest(".file-row, .grid-card");
  if(!row) return;
  if(e.target.closest("button") || e.target.tagName === "INPUT" || e.target.closest(".file-check") || e.target.closest(".grid-card-check")) return;
  const fp = row.dataset.path;
  const isDir = row.dataset.type === "dir";
  if(isDir) navigate(fp);
  else openFile(fp, currentEntries.find(en => joinPath(currentPath, en.name) === fp));
});

if(IS_ADMIN){
  fileListing.addEventListener("dragstart", e => {
    const row = e.target.closest(".file-row, .grid-card");
    if(!row) return;
    isInternalDrag = true;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", row.dataset.path);
    row.style.opacity = "0.5";
  });
  fileListing.addEventListener("dragend", e => {
    const row = e.target.closest(".file-row, .grid-card");
    if(!row) return;
    isInternalDrag = false;
    row.style.opacity = "";
  });
  fileListing.addEventListener("dragover", e => {
    const row = e.target.closest(".file-row, .grid-card");
    if(!row || row.dataset.type !== "dir") return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    row.classList.add("drop-target");
  });
  fileListing.addEventListener("dragleave", e => {
    const row = e.target.closest(".file-row, .grid-card");
    if(!row || row.dataset.type !== "dir") return;
    row.classList.remove("drop-target");
  });
  fileListing.addEventListener("drop", async e => {
    const row = e.target.closest(".file-row, .grid-card");
    if(!row || row.dataset.type !== "dir") return;
    e.preventDefault();
    e.stopPropagation();
    row.classList.remove("drop-target");
    
    if (!isInternalDrag) {
      await processDropItems(e, row.dataset.path);
      return;
    }
    
    const srcPath = e.dataTransfer.getData("text/plain");
    const fp = row.dataset.path;
    if(!srcPath || srcPath === fp) return;
    const name = srcPath.split("/").pop();
    await moveItem(srcPath, joinPath(fp, name));
  });
}
function openFile(fp,e){if(!e)e={name:fp.split("/").pop(),type:"file"};if(isVideo(e))openVideo(fp,e);else if(isAudio(e))openAudio(fp,e);else if(isImage(e))openImage(fp,e);else if(isText(e)||ext(e.name)===".pdf")openPreview(fp,e.name);else downloadFile(null,fp);}
function downloadFile(ev,fp){if(ev)ev.stopPropagation();const a=document.createElement("a");a.href=encPath(fp);a.download=fp.split("/").pop();a.click();}

function videoThumbFallback(img){
  const div = img.parentElement;
  div.innerHTML = `<div class="play-overlay" style="opacity:0.95"><svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>`;
}

function updateMediaList(){
  const activeEntries = filterEntriesByCategory(currentEntries);
  const sortedEntries = sortEntries(activeEntries);
  currentMediaList = sortedEntries.filter(e => {
    if(e.type === 'dir') return false;
    const x = ext(e.name);
    return VIDEO_EXTS.has(x) || IMAGE_EXTS.has(x);
  });
}

function getMediaCounterSuffix(){
  if(currentMediaList.length > 0 && currentMediaIndex >= 0){
    return ' (' + (currentMediaIndex + 1) + ' of ' + currentMediaList.length + ')';
  }
  return '';
}

function playMediaIndex(idx){
  if(!currentMediaList.length) return;
  currentMediaIndex = (idx + currentMediaList.length) % currentMediaList.length;
  const item = currentMediaList[currentMediaIndex];
  const fp = filePath(item);
  const x = ext(item.name);
  if(VIDEO_EXTS.has(x)){
    closeModal('modal-image');
    openVideo(fp, item);
  } else if(IMAGE_EXTS.has(x)){
    closeModal('modal-video');
    const player = document.getElementById('video-player');
    if(player) player.pause();
    openImage(fp, item);
  }
}

function navigateMedia(dir){
  updateMediaList();
  if(!currentMediaList.length) return;
  if(currentMediaIndex < 0) currentMediaIndex = 0;
  playMediaIndex(currentMediaIndex + dir);
}

function renderMarkdown(md){
  function escM(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
  function inline(s){
    s=escM(s);
    s=s.replace(/`([^`]+)`/g,"<code>$1</code>");
    s=s.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>");
    s=s.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g,"$1<em>$2</em>");
    s=s.replace(/(^|[^_])_([^_]+)_(?!_)/g,"$1<em>$2</em>");
    s=s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,(m,a,url)=>`<img src="${escM(url)}" alt="${escM(a)}">`);
    s=s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(m,a,url)=>`<a href="${escM(url)}">${a}</a>`);
    return s;
  }
  const lines=md.replace(/\r\n?/g,"\n").split("\n");
  let html="",i=0,inCode=false,codeBuf=[],listType="",inList=false;
  function closeList(){if(inList){html+=(listType==="ul"?"</ul>":"</ol>");inList=false;}}
  while(i<lines.length){
    const ln=lines[i];
    if(/^```/.test(ln)){closeList();
      if(inCode){html+="<pre><code>"+escM(codeBuf.join("\n"))+"</code></pre>";codeBuf=[];inCode=false;}
      else{inCode=true;codeBuf=[];}
      i++;continue;}
    if(inCode){codeBuf.push(ln);i++;continue;}
    if(!ln.trim()){closeList();html+="\n";i++;continue;}
    const h=ln.match(/^(#{1,6})\s+(.*)$/);
    if(h){closeList();html+=`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`;i++;continue;}
    if(/^(\s*[-*_]\s*){3,}\s*$/.test(ln)){closeList();html+="<hr>";i++;continue;}
    if(/^>\s?/.test(ln)){closeList();const b=ln.replace(/^>\s?/,"");html+=`<blockquote>${inline(b)}</blockquote>`;i++;continue;}
    const ul=ln.match(/^\s*[-*+]\s+(.*)$/);
    const ol=ln.match(/^\s*\d+[.)]\s+(.*)$/);
    if(ul||ol){const t=ul?"ul":"ol";if(!inList||listType!==t){closeList();html+=`<${t}>`;inList=true;listType=t;}html+=`<li>${inline(ul?ul[1]:ol[1])}</li>`;i++;continue;}
    closeList();
    let buf=[ln];i++;
    while(i<lines.length&&lines[i].trim()&&!/^#{1,6}\s/.test(lines[i])&&!/^```/.test(lines[i])&&!/^>\s?/.test(lines[i])&&!/^\s*[-*+]\s+/.test(lines[i])&&!/^\s*\d+[.)]\s+/.test(lines[i])){buf.push(lines[i]);i++;}
    html+=`<p>${buf.map(inline).join("<br>")}</p>`;
  }
  if(inCode){html+="<pre><code>"+escM(codeBuf.join("\n"))+"</code></pre>";}
  closeList();
  return html;
}

async function openPreview(fp,name){
  const body=document.getElementById("preview-body");
  document.getElementById("preview-title").textContent=name;
  document.getElementById("preview-download").onclick=()=>downloadFile(null,fp);
  const copyBtn=document.getElementById("preview-copy-link");
  if(copyBtn) copyBtn.onclick=()=>copyLink(null,fp);
  const editBtn=document.getElementById("preview-edit");
  if(editBtn){
    if(IS_ADMIN && isText({name:name})){
      editBtn.style.display="";
      editBtn.onclick=()=>{ closeModal("modal-preview"); editFile(null,fp,name); };
    } else {
      editBtn.style.display="none";
    }
  }
  body.innerHTML='<pre>Loading...</pre>';
  openModal("modal-preview");
  const x=ext(name);
  if(x===".pdf"){
    body.innerHTML=`<iframe src="${encPath(fp)}?preview=1"></iframe>`;
    return;
  }
  try{
    const r=await fetch(encPath(fp)+"?preview=1",{headers:{"Range":"bytes=0-1048575"}});
    const truncated=r.status===206;
    const t=await r.text();
    if(x===".md"){
      body.innerHTML=`<div class="markdown-body" style="padding:24px;max-width:860px;margin:0 auto;width:100%">${renderMarkdown(t)}</div>`;
    }else{
      body.innerHTML=`<pre>${esc(t)}</pre>`;
    }
    if(truncated)body.innerHTML+='<div class="preview-note">--- File truncated (showing first 1 MB). Use Download for the full file. ---</div>';
  }catch(err){
    body.innerHTML='<pre>Failed to load file</pre>';
  }
}

function openVideo(fp, e){
  updateMediaList();
  const name = typeof e === 'object' && e && e.name ? e.name : fp.split('/').pop();
  currentMediaIndex = currentMediaList.findIndex(item => item.name === name);
  const player = document.getElementById('video-player');
  player.src = encPath(fp) + '?preview=1';
  document.getElementById('video-title').textContent = name + getMediaCounterSuffix();
  document.getElementById('video-info').textContent = (e && e.size) ? humanSize(e.size) : '';
  const copyBtn = document.getElementById("video-copy-link");
  if(copyBtn) copyBtn.onclick = () => copyLink(null, fp);
  openModal('modal-video');
  player.load();
  player.play().catch(()=>{});
}

function openImage(fp, e){
  updateMediaList();
  const name = typeof e === 'object' && e && e.name ? e.name : fp.split('/').pop();
  currentMediaIndex = currentMediaList.findIndex(item => item.name === name);
  document.getElementById('image-title').textContent = name + getMediaCounterSuffix();
  const viewer = document.getElementById('image-viewer');
  viewer.style.opacity = '0.5';
  viewer.onload = () => { viewer.style.opacity = '1'; };
  viewer.src = encPath(fp) + '?preview=1';
  const copyBtn = document.getElementById("image-copy-link");
  if(copyBtn) copyBtn.onclick = () => copyLink(null, fp);
  openModal('modal-image');
}

function closeVideo(){const p=document.getElementById("video-player");p.pause();p.src="";closeModal("modal-video");}
function openAudio(fp,e){window.open(encPath(fp)+"?preview=1","_blank");}
async function editFile(ev,fp,name){
  if(ev)ev.stopPropagation();editorMode="edit";editorFilePath=fp;
  document.getElementById("editor-title").textContent="Edit: "+name;
  document.getElementById("editor-filename").value=name;document.getElementById("editor-filename").disabled=true;
  const ta=document.getElementById("editor-textarea");ta.value="Loading...";openModal("modal-editor");
  const r=await fetch(encPath(fp)+"?preview=1");ta.value=await r.text();updateEditorStatus();ta.focus();
}
function newFile(){editorMode="new";editorFilePath=null;document.getElementById("editor-title").textContent="New file";document.getElementById("editor-filename").value="";document.getElementById("editor-filename").disabled=false;document.getElementById("editor-textarea").value="";updateEditorStatus();openModal("modal-editor");setTimeout(()=>document.getElementById("editor-filename").focus(),100);}
function updateEditorStatus(){const ta=document.getElementById("editor-textarea");document.getElementById("editor-lines").textContent=ta.value.split(String.fromCharCode(10)).length+" lines";document.getElementById("editor-chars").textContent=ta.value.length+" chars";}
function editorIndent(){const ta=document.getElementById("editor-textarea");const s=ta.selectionStart,e=ta.selectionEnd;ta.value=ta.value.slice(0,s)+"  "+ta.value.slice(e);ta.selectionStart=ta.selectionEnd=s+2;}
function editorWrap(before,after){const ta=document.getElementById("editor-textarea");const s=ta.selectionStart,e=ta.selectionEnd;const sel=ta.value.slice(s,e);ta.value=ta.value.slice(0,s)+before+sel+after+ta.value.slice(e);ta.selectionStart=s+before.length;ta.selectionEnd=s+before.length+sel.length;}
document.getElementById("editor-textarea").addEventListener("input",updateEditorStatus);
document.getElementById("editor-textarea").addEventListener("keydown",e=>{if(e.key==="Tab"){e.preventDefault();editorIndent();}if((e.ctrlKey||e.metaKey)&&e.key==="s"){e.preventDefault();saveFile();}});
document.getElementById("editor-save").addEventListener("click",saveFile);
async function saveFile(){
  const ta=document.getElementById("editor-textarea");const content=ta.value;let fp;
  if(editorMode==="edit"){fp=editorFilePath;}else{const name=document.getElementById("editor-filename").value.trim();if(!name){notify("Enter a filename","error");return;}fp=joinPath(currentPath,name);}
  const encoded=new TextEncoder().encode(content);
  const r=await fetch(encPath(fp),{method:"PUT",headers:{"Content-Length":String(encoded.length)},body:encoded});
  if(r.status===201||r.status===200){notify("Saved","success");closeModal("modal-editor");loadDir(currentPath);}
  else notify("Save failed: "+r.status,"error");
}
function toggleSelect(ev,fp){ev.stopPropagation();if(selected.has(fp))selected.delete(fp);else selected.add(fp);updateBulkActions();renderEntries(currentEntries);}
function toggleAll(ev){ev.stopPropagation();if(ev.target.checked)currentEntries.forEach(e=>selected.add(filePath(e)));else selected.clear();updateBulkActions();renderEntries(currentEntries);}
function updateBulkActions(){const n=selected.size;const bulk=document.getElementById("bulk-actions");if(n>0){bulk.classList.add("active");document.getElementById("sel-count").textContent=n+" selected";}else bulk.classList.remove("active");}
document.getElementById("btn-deselect").addEventListener("click",()=>{selected.clear();updateBulkActions();renderEntries(currentEntries);});
document.getElementById("btn-download-sel").addEventListener("click",async()=>{const paths=[...selected];if(!paths.length)return;const d=await api("POST",API_BASE+"_api/zip",{paths});if(d.key){const a=document.createElement("a");a.href=`${API_BASE}_api/zip-dl?key=${d.key}`;a.download=d.filename||"download.zip";a.click();}else notify(d.error||"Failed","error");});
document.getElementById("btn-copy-sel").addEventListener("click",()=>{const paths=[...selected];if(!paths.length)return;const urls=paths.map(p=>location.origin+encPath(p.startsWith("/")?p:"/"+p)).join("\n");if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(urls).then(()=>{notify(`Copied ${paths.length} link(s) to clipboard`,"success");}).catch(()=>fallbackCopy(urls));}else{fallbackCopy(urls);}});
function confirmDelete(ev,paths){if(ev)ev.stopPropagation();pendingDeletePaths=paths;const n=paths.length;document.getElementById("delete-msg").textContent=`Delete ${n} item${n!==1?"s":""}? This cannot be undone.`;openModal("modal-delete");}
document.getElementById("delete-confirm").addEventListener("click",async()=>{const d=await api("POST",API_BASE+"_api/delete",{paths:pendingDeletePaths});if(d.deleted)notify(`Deleted ${d.deleted.length} item(s)`,"success");if(d.errors&&d.errors.length)notify("Some items failed to delete","error");selected.clear();updateBulkActions();closeModal("modal-delete");loadDir(currentPath);});
document.getElementById("btn-delete-sel").addEventListener("click",()=>{if(!selected.size)return;confirmDelete(null,[...selected]);});
function startRename(ev,fp,name){if(ev)ev.stopPropagation();renameFromPath=fp;document.getElementById("rename-val").value=name;openModal("modal-rename");setTimeout(()=>{const i=document.getElementById("rename-val");i.focus();i.select();},100);}
document.getElementById("rename-submit").addEventListener("click",async()=>{const newName=document.getElementById("rename-val").value.trim();if(!newName)return;const dir=renameFromPath.substring(0,renameFromPath.lastIndexOf("/"))||"/";const dst=joinPath(dir,newName);const d=await api("POST",API_BASE+"_api/rename",{"from":renameFromPath,to:dst});if(d.ok){notify("Renamed","success");closeModal("modal-rename");loadDir(currentPath);}else notify(d.error||"Rename failed","error");});
async function startMoveOne(ev,fp){if(ev)ev.stopPropagation();movePaths=[fp];await openMoveModal();}
document.getElementById("btn-move-sel").addEventListener("click",async()=>{if(!selected.size)return;movePaths=[...selected];await openMoveModal();});
async function openMoveModal(){moveTargetPath="/";await renderMoveTree();openModal("modal-move");}
function treeNode(depth){
  const item=document.createElement("div");
  item.className="tree-item";item.style.paddingLeft=(12+depth*16)+"px";
  item.innerHTML=`<span class="tree-chevron">&#9656;</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 012-2h3.586a1 1 0 01.707.293L11 7h10a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg><span class="tree-label"></span>`;
  return item;
}
async function renderMoveTree(){
  const tree=document.getElementById("move-tree");tree.innerHTML="";
  const root=document.createElement("div");
  root.className="tree-item"+(moveTargetPath==="/"?" active":"");
  root.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>/ (root)`;
  root.addEventListener("click",()=>selectMoveTarget("/",root));tree.appendChild(root);
  const rootHolder=document.createElement("div");
  root.after(rootHolder);
  await loadSubDirs("/",rootHolder,1);
}
async function loadSubDirs(path,holder,depth){
  holder.innerHTML='<div class="tree-item tree-loading" style="padding-left:'+(12+depth*16)+'px;color:var(--text2);font-size:12px">Loading...</div>';
  const d=await api("GET",`${API_BASE}_api/list?path=${encodeURIComponent(path)}&dirs=1`);
  holder.innerHTML="";
  if(!d || d.error)return;
  const dirs=(d.entries||[]).filter(e=>e.type==="dir");
  for(const dir of dirs){
    const dp=joinPath(path,dir.name);
    const item=treeNode(depth);
    item.querySelector(".tree-label").textContent=dir.name;
    item.addEventListener("click",()=>selectMoveTarget(dp,item));
    holder.appendChild(item);
    if(dir.has_dirs){
      const chevron=item.querySelector(".tree-chevron");
      chevron.classList.add("expandable");
      chevron.addEventListener("click",ev=>{ev.stopPropagation();toggleDir(item,dp,depth);});
    }
  }
}
function toggleDir(item,path,depth){
  let holder=item.querySelector(".tree-children");
  if(!holder){
    holder=document.createElement("div");
    holder.className="tree-children";
    item.after(holder);
  }
  const chevron=item.querySelector(".tree-chevron");
  if(item.dataset.open==="1"){
    item.dataset.open="0";chevron.classList.remove("open");
    holder.style.display="none";
    return;
  }
  item.dataset.open="1";chevron.classList.add("open");
  if(holder.dataset.loaded==="1"){
    holder.style.display="";
    return;
  }
  holder.dataset.loaded="1";
  loadSubDirs(path,holder,depth+1);
}
function selectMoveTarget(dp,item){moveTargetPath=dp;document.querySelectorAll(".tree-item").forEach(i=>i.classList.remove("active"));item.classList.add("active");}
document.getElementById("move-submit").addEventListener("click",async()=>{
  if(!movePaths.length)return;let ok=0,fail=0;
  for(const src of movePaths){const name=src.split("/").pop();const dst=joinPath(moveTargetPath,name);if(dst===src){fail++;continue;}const d=await api("POST",API_BASE+"_api/rename",{"from":src,to:dst});if(d.ok)ok++;else fail++;}
  if(ok)notify(`Moved ${ok} item(s)`,"success");if(fail)notify(`${fail} item(s) failed`,"error");
  selected.clear();updateBulkActions();closeModal("modal-move");loadDir(currentPath);
});
async function moveItem(src,dst){if(src===dst)return;const d=await api("POST",API_BASE+"_api/rename",{"from":src,to:dst});if(d.ok){notify("Moved","success");loadDir(currentPath);}else notify(d.error||"Move failed","error");}
document.getElementById("btn-mkdir").addEventListener("click",()=>{document.getElementById("mkdir-name").value="";openModal("modal-mkdir");setTimeout(()=>document.getElementById("mkdir-name").focus(),100);});
document.getElementById("mkdir-submit").addEventListener("click",async()=>{const name=document.getElementById("mkdir-name").value.trim();if(!name)return;const d=await api("POST",API_BASE+"_api/mkdir",{path:joinPath(currentPath,name)});if(d.ok){notify("Folder created","success");closeModal("modal-mkdir");loadDir(currentPath);}else notify(d.error||"Failed","error");});
document.getElementById("btn-newfile").addEventListener("click",newFile);
const PARALLEL_UPLOADS=4;const CHUNK_SIZE=2*1024*1024;
function getIconForFile(name){const x=(name.lastIndexOf(".")>=0?name.slice(name.lastIndexOf(".")):"").toLowerCase();if(VIDEO_EXTS.has(x))return"🎬";if(AUDIO_EXTS.has(x))return"🎵";if(IMAGE_EXTS.has(x))return"🖼️";return"📄";}
let uploadQueueTimer = null;

function closeUploadQueue(){
  const queue = document.getElementById("upload-queue");
  queue.classList.remove("active");
  if(uploadQueueTimer) clearTimeout(uploadQueueTimer);
}

async function uploadFiles(files){
  if(!files||!files.length) return;
  if(uploadQueueTimer) clearTimeout(uploadQueueTimer);
  const queue = document.getElementById("upload-queue");
  const container = document.getElementById("upload-queue-items");
  container.innerHTML = "";
  document.getElementById("upload-queue-title").textContent = "Uploading files...";
  queue.classList.add("active");
  
  const fileArr = [...files];
  const items = fileArr.map((f,i) => {
    const id = "upl-" + Date.now() + "-" + i;
    const div = document.createElement("div");
    div.className = "upload-item";
    div.id = id;
    div.innerHTML = `<div class="upload-item-icon">${getIconForFile(f.name)}</div><div class="upload-item-info"><div class="upload-item-name">${esc(f.name)}</div><div class="upload-item-meta">${humanSize(f.size)}</div><div class="upload-progress"><div class="upload-progress-bar" id="${id}-bar"></div></div></div><div class="upload-status" id="${id}-status">Queued</div>`;
    container.appendChild(div);
    return {file:f, id};
  });

  let hasError = false;
  for(let i=0; i<items.length; i+=PARALLEL_UPLOADS){
    const batch = items.slice(i, i+PARALLEL_UPLOADS);
    const results = await Promise.all(batch.map(item => uploadOne(item)));
    if(results.some(r => r === false)) hasError = true;
  }

  loadDir(currentPath);

  if(!hasError){
    document.getElementById("upload-queue-title").textContent = "Upload complete";
    notify("Upload completed", "success");
    uploadQueueTimer = setTimeout(() => {
      closeUploadQueue();
    }, 2000);
  } else {
    document.getElementById("upload-queue-title").textContent = "Upload finished with errors";
  }
}

async function uploadOne({file,id}){
  const bar = document.getElementById(id+"-bar"), status = document.getElementById(id+"-status");
  const tDir = file.targetDir || currentPath;
  const targetPath = joinPath(tDir, file.relativePath || file.name);
  const url = encPath(targetPath);
  status.textContent = "Uploading...";
  try{
    const total = file.size;
    if(total === 0){
      const r = await fetch(url, {method:"PUT", headers:{"Content-Length":"0"}, body:new Uint8Array(0)});
      if(r.ok || r.status===201){
        bar.style.width = "100%";
        bar.classList.add("success");
        status.textContent = "Done";
        return true;
      } else {
        bar.classList.add("error");
        status.textContent = "Error";
        return false;
      }
    }
    let offset = 0;
    while(offset < total){
      const end = Math.min(offset + CHUNK_SIZE, total) - 1;
      const slice = file.slice(offset, end + 1);
      const r = await fetch(url, {
        method: "PUT",
        headers: {
          "Content-Range": `bytes ${offset}-${end}/${total}`,
          "Content-Length": String(end - offset + 1)
        },
        body: slice
      });
      if(!r.ok) throw new Error("Server error " + r.status);
      offset = end + 1;
      const pct = Math.round(offset / total * 100);
      bar.style.width = pct + "%";
      status.textContent = pct + "%";
    }
    bar.classList.add("success");
    status.textContent = "Done";
    return true;
  } catch(e){
    bar.classList.add("error");
    status.textContent = "Failed";
    notify("Upload failed: " + file.name, "error");
    return false;
  }
}
const dropZone=document.getElementById("drop-zone"),fileInput=document.getElementById("file-input");
document.getElementById("btn-upload").addEventListener("click",()=>fileInput.click());
dropZone.addEventListener("click",()=>fileInput.click());
fileInput.addEventListener("change",e=>{uploadFiles(e.target.files);fileInput.value="";});
document.addEventListener("paste",e=>{
  if(!IS_ADMIN)return;
  const t=e.target;
  if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.isContentEditable))return;
  const items=e.clipboardData&&e.clipboardData.items;
  if(!items)return;
  const files=[];
  for(const it of items){
    if(it.kind!=="file")continue;
    const f=it.getAsFile();
    if(!f)continue;
    if(f.name==="image.png"||!f.name){
      const d=new Date();
      const ts=d.getFullYear()+String(d.getMonth()+1).padStart(2,"0")+String(d.getDate()).padStart(2,"0")+"_"+String(d.getHours()).padStart(2,"0")+String(d.getMinutes()).padStart(2,"0")+String(d.getSeconds()).padStart(2,"0");
      const ext2=f.type?("."+f.type.split("/")[1]):".png";
      files.push(new File([f],"paste_"+ts+ext2,{type:f.type}));
    }else files.push(f);
  }
  if(files.length){notify("Pasting image","info");uploadFiles(files);}
});
async function processDropItems(e, targetDir) {
  const items = e.dataTransfer.items;
  const filesToUpload = [];
  if (!items || !items.length) {
    const files = e.dataTransfer.files;
    if (files && files.length) {
      const validFiles = Array.from(files).filter(f => !(f.size === 0 && !f.type && f.name.indexOf('.') === -1));
      validFiles.forEach(f => { f.targetDir = targetDir; filesToUpload.push(f); });
      if (validFiles.length) uploadFiles(validFiles);
    }
    return;
  }
  
  async function traverseEntry(entry, relPath = "") {
    if (entry.isFile) {
      const file = await new Promise((resolve) => entry.file(resolve));
      file.relativePath = relPath + file.name;
      file.targetDir = targetDir;
      filesToUpload.push(file);
    } else if (entry.isDirectory) {
      const dirReader = entry.createReader();
      const readEntries = async () => new Promise(resolve => dirReader.readEntries(resolve));
      let entries = await readEntries();
      let allEntries = [...entries];
      while (entries.length > 0) {
        entries = await readEntries();
        if (entries.length === 0) break;
        allEntries = allEntries.concat(entries);
      }
      for (const child of allEntries) {
        await traverseEntry(child, relPath + entry.name + "/");
      }
    }
  }
  
  const traversePromises = [];
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.kind === 'file') {
      const entry = typeof item.webkitGetAsEntry === 'function' ? item.webkitGetAsEntry() : null;
      if (entry) traversePromises.push(traverseEntry(entry));
      else {
        const f = item.getAsFile();
        if(f && !(f.size === 0 && !f.type && f.name.indexOf('.') === -1)) {
          f.targetDir = targetDir;
          filesToUpload.push(f);
        }
      }
    }
  }
  await Promise.all(traversePromises);
  if (filesToUpload.length) uploadFiles(filesToUpload);
}

async function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  if (isInternalDrag) return;
  dropZone.classList.remove("drag-over");
  await processDropItems(e, currentPath);
}

document.addEventListener("dragover", e => e.preventDefault());
document.addEventListener("drop", handleDrop);
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove("drag-over");
  handleDrop(e);
});
document.getElementById("view-list").addEventListener("click",()=>{viewMode="list";localStorage.setItem("viewMode","list");document.getElementById("view-list").classList.add("active");document.getElementById("view-grid").classList.remove("active");renderEntries(currentEntries);});
document.getElementById("view-grid").addEventListener("click",()=>{viewMode="grid";localStorage.setItem("viewMode","grid");document.getElementById("view-grid").classList.add("active");document.getElementById("view-list").classList.remove("active");renderEntries(currentEntries);});
function setSort(key){if(sortKey===key)sortAsc=!sortAsc;else{sortKey=key;sortAsc=true;}renderEntries(currentEntries);updateMediaList();}
document.getElementById("search").addEventListener("input",e=>{
  clearTimeout(searchTimer);const q=e.target.value.trim();
  if(!q){loadDir(currentPath);return;}
  searchTimer=setTimeout(async()=>{const d=await api("GET",`${API_BASE}_api/search?q=${encodeURIComponent(q)}&path=${encodeURIComponent(currentPath)}`);if(d.results){currentEntries=d.results.map(r=>({...r,name:r.name}));renderEntries(currentEntries);updateMediaList();}},350);
});
function openModal(id){document.getElementById(id).classList.add("active");}
function closeModal(id){document.getElementById(id).classList.remove("active");}
document.querySelectorAll(".modal-overlay").forEach(overlay=>{overlay.addEventListener("click",e=>{if(e.target===overlay)overlay.classList.remove("active");});});
document.addEventListener("keydown",e=>{
  const activeVideo = document.getElementById("modal-video").classList.contains("active");
  const activeImage = document.getElementById("modal-image").classList.contains("active");
  if(activeVideo || activeImage){
    if(e.key === "ArrowLeft"){ e.preventDefault(); navigateMedia(-1); return; }
    if(e.key === "ArrowRight"){ e.preventDefault(); navigateMedia(1); return; }
  }
  if(e.key==="Escape"){
    document.querySelectorAll(".modal-overlay.active").forEach(m=>{
      if(m.id==="modal-video")closeVideo();
      else m.classList.remove("active");
    });
  }
});
document.getElementById("mkdir-name").addEventListener("keydown",e=>{if(e.key==="Enter")document.getElementById("mkdir-submit").click();});
document.getElementById("rename-val").addEventListener("keydown",e=>{if(e.key==="Enter")document.getElementById("rename-submit").click();});
if(IS_ADMIN){document.getElementById("btn-upload").style.display="";document.getElementById("btn-mkdir").style.display="";document.getElementById("btn-newfile").style.display="";document.getElementById("drop-zone").style.display="";document.getElementById("btn-logout").style.display="";}
else{document.getElementById("btn-move-sel").style.display="none";document.getElementById("btn-delete-sel").style.display="none";}
document.getElementById("btn-logout").addEventListener("click",async()=>{await api("POST",API_BASE+"_api/logout");location.href=API_BASE+"_login";});
if(viewMode==="grid"){document.getElementById("view-grid").classList.add("active");document.getElementById("view-list").classList.remove("active");}
window.addEventListener("popstate", e => {
  let p = (e.state && e.state.path);
  if(!p){
    p = decodeURIComponent(location.pathname);
    if(API_BASE && API_BASE !== "/" && p.startsWith(API_BASE)){
      p = "/" + p.substring(API_BASE.length);
    }
    let idx = p.indexOf("/_ui");
    if(idx >= 0) p = p.substring(idx + 4);
    if(!p || p === "/_login" || p.trim() === "") p = "/";
  }
  if(!p.startsWith("/")) p = "/" + p;
  navigate(p, false);
});
renderRecent();
function toggleSidebar(){
  const s=document.getElementById("sidebar");
  const o=document.getElementById("sidebar-overlay");
  if(s.classList.contains("active")){
    s.classList.remove("active");o.classList.remove("active");
  }else{
    s.classList.add("active");o.classList.add("active");
  }
}
function closeSidebar(){
  const s=document.getElementById("sidebar");
  const o=document.getElementById("sidebar-overlay");
  if(s) s.classList.remove("active");
  if(o) o.classList.remove("active");
}
function openBottomSheet(event, fp, name, isDir, isTextFile) {
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }
  const title = document.getElementById("sheet-title");
  const content = document.getElementById("sheet-content");
  title.textContent = name;
  
  let html = "";
  if (IS_ADMIN && isTextFile) {
    html += `<button class="bottom-sheet-item" onclick="closeSheet('sheet-actions'); editFile(null, ${jesc(fp)}, ${jesc(name)})">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
      <span>Edit File</span>
    </button>`;
  }
  if (IS_ADMIN) {
    html += `<button class="bottom-sheet-item" onclick="closeSheet('sheet-actions'); startRename(null, ${jesc(fp)}, ${jesc(name)})">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z"></path></svg>
      <span>Rename</span>
    </button>`;
    html += `<button class="bottom-sheet-item" onclick="closeSheet('sheet-actions'); startMoveOne(null, ${jesc(fp)})">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 9 2 12 5 15"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"></line></svg>
      <span>Move</span>
    </button>`;
  }
  html += `<button class="bottom-sheet-item" onclick="closeSheet('sheet-actions'); copyLink(null, ${jesc(fp)})">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
    <span>Copy Link</span>
  </button>`;
  if (!isDir) {
    html += `<button class="bottom-sheet-item" onclick="closeSheet('sheet-actions'); downloadFile(null, ${jesc(fp)})">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"></line></svg>
      <span>Download</span>
    </button>`;
  }
  if (IS_ADMIN) {
    html += `<button class="bottom-sheet-item danger" onclick="closeSheet('sheet-actions'); confirmDelete(null, [${jesc(fp)}])">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"></path></svg>
      <span>Delete</span>
    </button>`;
  }
  
  content.innerHTML = html;
  document.getElementById("sheet-actions").classList.add("active");
}
function closeSheet(id) {
  document.getElementById(id).classList.remove("active");
}
const API_BASE = (function(){
  let p = location.pathname;
  let idx = p.indexOf('/_ui');
  if(idx >= 0) {
    p = p.substring(0, idx);
    return p.endsWith('/') ? p : p + '/';
  }
  if(p.endsWith('.py') || p.endsWith('.html') || p.endsWith('.php')) {
    p = p.substring(0, p.lastIndexOf('/'));
    return p.endsWith('/') ? p : p + '/';
  }
  return '/';
})();
(function(){
  let p = decodeURIComponent(location.pathname);
  if(API_BASE && API_BASE !== '/' && p.startsWith(API_BASE)){
    p = '/' + p.substring(API_BASE.length);
  }
  let idx = p.indexOf('/_ui');
  if(idx >= 0){
    p = p.substring(idx + 4);
  }
  if(!p || p === '/_login' || p.trim() === '') p = '/';
  if(!p.startsWith('/')) p = '/' + p;
  history.replaceState({path: p}, "", location.href);
  navigate(p, false);
})();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    base_dir:    str  = os.getcwd()
    auth_user:   str  = ""
    auth_pass:   str  = ""
    max_upload:  int  = 10 * 1024 ** 3
    nginx_accel_prefix: str = ""
    public_mode: bool = False
    force_https: bool = False
    https_port:  int  = 443
    thumb_dir:   str  = THUMB_DIR
    timeout:     int  = 60

    def log_message(self, fmt, *args): pass
    def log_error(self, fmt, *args): pass

    def _get_session_token(self):
        for part in self.headers.get("Cookie","").split(";"):
            part = part.strip()
            if part.startswith("session="):
                return part[8:]
        return None

    def _check_auth(self, require_admin=False):
        if not self.auth_user: return True
        if self.public_mode and not require_admin: return True
        auth = self.headers.get("Authorization","")
        if auth.startswith("Basic "):
            try:
                u, p = base64.b64decode(auth.split(None,1)[1]).decode().split(":",1)
                if u == self.auth_user and p == self.auth_pass: return True
            except Exception: pass
        token = self._get_session_token()
        if token and validate_session(token): return True
        if not require_admin and "text/html" in self.headers.get("Accept",""):
            self.send_response(302)
            self.send_header("Location", f"/_login?next={urllib.parse.quote(self.path)}")
            self.end_headers(); return False
        self._send_401(); return False

    def _send_401(self):
        if "/_api/" in self.path:
            return self._json({"error":"Authentication required"}, 401)
        body = b"Authentication required\n"
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="FileStation"')
        self.send_header("Content-Type","text/plain")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def _enforce_https(self):
        if not getattr(self,"force_https",False): return False
        if isinstance(self.connection, ssl.SSLSocket): return False
        host = self.headers.get("Host","")
        if not host: return False
        domain = host.split(":")[0]
        port_str = f":{self.https_port}" if self.https_port != 443 else ""
        self.send_response(301)
        self.send_header("Location", f"https://{domain}{port_str}{self.path}")
        self.end_headers(); return True

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers(); self.wfile.write(body)

    def _json_with_cookie(self, obj, cookie_str, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Set-Cookie", cookie_str)
        self.end_headers(); self.wfile.write(body)

    def _html(self, html, status=200):
        body = html.encode() if isinstance(html,str) else html
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","same-origin")
        self.send_header("Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: blob:; media-src 'self' blob:; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        self.end_headers(); self.wfile.write(body)

    def _text(self, text, status=200):
        body = text.encode() if isinstance(text,str) else text
        self.send_response(status)
        self.send_header("Content-Type","text/plain; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers(); self.wfile.write(body)

    def _read_json(self, max_len=1048576):
        length = int(self.headers.get("Content-Length",0))
        if length > max_len: return None
        try: return json.loads(self.rfile.read(length))
        except Exception: return None

    def _resolve(self, url_path):
        decoded = urllib.parse.unquote(url_path).lstrip("/")
        return safe_path(self.base_dir, decoded)

    def _api_login(self):
        data = self._read_json()
        if not data: return self._json({"error":"Invalid request"},400)
        if data.get("username")==self.auth_user and data.get("password")==self.auth_pass:
            token = create_session(data["username"])
            cookie = "session="+token+"; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400"
            return self._json_with_cookie({"ok":True}, cookie)
        return self._json({"error":"Invalid credentials"},401)

    def _api_logout(self):
        token = self._get_session_token()
        if token: destroy_session(token)
        return self._json_with_cookie({"ok":True},"session=; Path=/; HttpOnly; Max-Age=0")

    def _api_list(self, dir_path, dirs_only=False):
        fs = self._resolve(dir_path)
        if not fs or not os.path.isdir(fs): return self._json({"error":"Not found"},404)
        entries = []
        try:
            with os.scandir(fs) as it:
                scanned = sorted(it, key=lambda entry: entry.name)
                for entry in scanned:
                    name = entry.name
                    try: st = entry.stat(follow_symlinks=False)
                    except OSError: continue
                    if entry.is_dir(follow_symlinks=False):
                        e = {"name": name, "modified": st.st_mtime, "type": "dir"}
                        if dirs_only:
                            e["has_dirs"] = False
                            try:
                                with os.scandir(entry.path) as sub_it:
                                    for sub in sub_it:
                                        if sub.is_dir(follow_symlinks=False):
                                            e["has_dirs"] = True
                                            break
                            except (PermissionError, OSError):
                                pass
                        else:
                            try:
                                with os.scandir(entry.path) as sub_it:
                                    cnt = 0
                                    for _ in sub_it:
                                        cnt += 1
                                        if cnt >= 1000: break
                                    e["children"] = cnt
                            except (PermissionError, OSError):
                                e["children"] = 0
                        entries.append(e)
                    else:
                        if dirs_only: continue
                        e = {"name": name, "modified": st.st_mtime, "type": "file",
                             "size": st.st_size, "ext": os.path.splitext(name)[1].lower()}
                        entries.append(e)
        except PermissionError: return self._json({"error":"Permission denied"},403)
        if dirs_only:
            self._json({"path":dir_path,"entries":entries})
        else:
            self._json({"path":dir_path,"entries":entries,"disk":disk_info(fs)})

    def _api_search(self, query, base):
        fs = self._resolve(base)
        if not fs or not os.path.isdir(fs): return self._json({"error":"Not found"},404)
        results, ql = [], query.lower()
        scanned = 0
        for root, dirs, files in os.walk(fs):
            if scanned >= 100000: break
            for name in dirs + files:
                scanned += 1
                if scanned >= 100000: break
                if ql in name.lower():
                    fp = os.path.join(root, name)
                    try: st = os.stat(fp)
                    except OSError: continue
                    r = {"name":name,"path":"/"+os.path.relpath(fp,self.base_dir),"modified":st.st_mtime}
                    r["type"]="dir" if os.path.isdir(fp) else "file"
                    if r["type"]=="file": r["size"]=st.st_size; r["ext"]=os.path.splitext(name)[1].lower()
                    results.append(r)
                    if len(results)>=200: break
            if len(results)>=200: break
        self._json({"query":query,"results":results})

    def _api_delete(self):
        data = self._read_json()
        if not data: return self._json({"error":"Invalid request"},400)
        deleted, errors = [], []
        base_real = os.path.realpath(self.base_dir)
        for p in data.get("paths",[]):
            fs = self._resolve(p)
            if not fs or fs==base_real: errors.append({"path":p,"error":"Invalid path"}); continue
            try:
                if os.path.isdir(fs): shutil.rmtree(fs)
                elif os.path.isfile(fs) or os.path.islink(fs): os.remove(fs)
                else: errors.append({"path":p,"error":"Not found"}); continue
                deleted.append(p)
            except OSError as e: errors.append({"path":p,"error":str(e)})
        self._json({"deleted":deleted,"errors":errors})

    def _api_rename(self):
        data = self._read_json()
        if not data: return self._json({"error":"Invalid request"},400)
        src, dst = data.get("from",""), data.get("to","")
        if not src or not dst: return self._json({"error":"Missing from/to"},400)
        src_fs, dst_fs = self._resolve(src), self._resolve(dst)
        if not src_fs or not dst_fs: return self._json({"error":"Invalid path"},400)
        if not os.path.exists(src_fs): return self._json({"error":"Source not found"},404)
        if os.path.exists(dst_fs): return self._json({"error":"Destination exists"},409)
        try:
            os.makedirs(os.path.dirname(dst_fs), exist_ok=True)
            shutil.move(src_fs, dst_fs); self._json({"ok":True})
        except OSError as e: self._json({"error":str(e)},500)

    def _api_mkdir(self):
        data = self._read_json()
        if not data: return self._json({"error":"Invalid request"},400)
        path = data.get("path","")
        if not path: return self._json({"error":"Missing path"},400)
        fs = self._resolve(path)
        if not fs: return self._json({"error":"Invalid path"},400)
        if os.path.exists(fs): return self._json({"error":"Already exists"},409)
        try: os.makedirs(fs); self._json({"ok":True})
        except OSError as e: self._json({"error":str(e)},500)

    def _api_zip_prepare(self):
        data = self._read_json()
        if not data: return self._json({"error":"Invalid request"},400)
        paths = data.get("paths",[])
        if not paths: return self._json({"error":"No paths specified"},400)
        resolved = []
        for p in paths:
            fs = self._resolve(p)
            if not fs or not os.path.exists(fs): return self._json({"error":"Path not found: "+p},404)
            resolved.append(fs)
        key = secrets.token_urlsafe(16)
        _zip_keys[key] = {"paths":resolved,"created":time.time()}
        filename = os.path.basename(resolved[0])+".zip" if len(resolved)==1 else "download.zip"
        cleanup_old(); return self._json({"key":key,"filename":filename})

    def _serve_zip(self, key):
        entry = _zip_keys.get(key)
        if not entry: return self._json({"error":"Invalid or expired download key"},404)
        if time.time()-entry["created"]>300:
            _zip_keys.pop(key, None)
            return self._json({"error":"Download key expired"},410)
        paths = entry["paths"]
        tmp = tempfile.SpooledTemporaryFile(max_size=64*1024*1024)
        try:
            with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as zf:
                for fspath in paths:
                    if os.path.isfile(fspath): zf.write(fspath, os.path.basename(fspath))
                    elif os.path.isdir(fspath):
                        dirname = os.path.basename(fspath)
                        for root, dirs, files in os.walk(fspath):
                            for fname in files:
                                full = os.path.join(root, fname)
                                zf.write(full, os.path.join(dirname, os.path.relpath(full, fspath)))
            tmp.seek(0,2); size = tmp.tell(); tmp.seek(0)
            dl_name = os.path.basename(paths[0])+".zip" if len(paths)==1 else "download.zip"
            self.send_response(200)
            self.send_header("Content-Type","application/zip")
            self.send_header("Content-Disposition",f'attachment; filename="{dl_name}"')
            self.send_header("Content-Length",str(size))
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            while True:
                chunk = tmp.read(CHUNK)
                if not chunk: break
                try: self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError): break
        finally: tmp.close()

    def _serve_file(self, fs_path, head_only=False):
        try: st = os.stat(fs_path)
        except OSError: return self.send_error(404)
        fsize = st.st_size; ctype = mime_type(fs_path)
        etag = f'"{int(st.st_mtime)}-{st.st_size}"'
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304); self.end_headers(); return
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        is_preview = bool(qs.get("preview"))
        if self.nginx_accel_prefix:
            rel = os.path.relpath(fs_path, self.base_dir)
            accel_uri = join_path(self.nginx_accel_prefix, rel) if 'join_path' in globals() else f"{self.nginx_accel_prefix.rstrip('/')}/{rel.lstrip('/')}"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "private, max-age=86400")
            self.send_header("X-Accel-Redirect", accel_uri)
            if not is_preview: self.send_header("Content-Disposition", f'attachment; filename="{urllib.parse.quote(os.path.basename(fs_path))}"')
            self.end_headers(); return
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        is_preview = bool(qs.get("preview"))
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            try:
                spec = rng[6:]
                if spec.startswith("-"): start, end = max(0,fsize-int(spec[1:])), fsize-1
                elif spec.endswith("-"): start, end = int(spec[:-1]), fsize-1
                else: parts=spec.split("-",1); start,end=int(parts[0]),int(parts[1])
                if start>end or start>=fsize:
                    self.send_response(416); self.send_header("Content-Range",f"bytes */{fsize}"); self.end_headers(); return
                end=min(end,fsize-1); length=end-start+1
                self.send_response(206)
                self.send_header("Content-Type",ctype)
                self.send_header("Content-Length",str(length))
                self.send_header("Content-Range",f"bytes {start}-{end}/{fsize}")
                self.send_header("Accept-Ranges","bytes")
                self.send_header("Last-Modified",self.date_time_string(st.st_mtime))
                self.send_header("ETag", etag)
                self.send_header("Cache-Control","private, max-age=86400")
                self.send_header("X-Content-Type-Options","nosniff")
                if not is_preview: self.send_header("Content-Disposition",f'attachment; filename="{urllib.parse.quote(os.path.basename(fs_path))}"')
                self.end_headers()
                if head_only: return
                with open(fs_path,"rb") as f:
                    f.seek(start); rem=length
                    while rem>0:
                        chunk=f.read(min(CHUNK,rem))
                        if not chunk: break
                        try: self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError): break
                        rem -= len(chunk)
                return
            except (ValueError, IndexError): pass
        self.send_response(200)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(fsize))
        self.send_header("Accept-Ranges","bytes")
        self.send_header("Last-Modified",self.date_time_string(st.st_mtime))
        self.send_header("ETag", etag)
        self.send_header("Cache-Control","private, max-age=86400")
        self.send_header("X-Content-Type-Options","nosniff")
        if not is_preview: self.send_header("Content-Disposition",f'attachment; filename="{urllib.parse.quote(os.path.basename(fs_path))}"')
        self.end_headers()
        if head_only: return
        with open(fs_path,"rb") as f:
            while True:
                chunk=f.read(CHUNK)
                if not chunk: break
                try: self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError): break

    def _is_video(self, fs_path):
        return mime_type(fs_path).startswith("video/")

    def _serve_thumb(self, fs_path):
        try:
            st = os.stat(fs_path)
            if st.st_size < 1024:
                return self.send_error(404)
        except OSError:
            return self.send_error(404)
        try:
            os.makedirs(self.thumb_dir, exist_ok=True)
            key = hashlib.sha1(f"{os.path.realpath(fs_path)}:{st.st_mtime}:{st.st_size}".encode()).hexdigest()
            out = os.path.join(self.thumb_dir, key + ".jpg")
            if not os.path.exists(out):
                probe = subprocess.run(
                    ["ffprobe","-v","error","-select_streams","v:0","-show_entries",
                     "format=duration","-of","default=noprint_wrappers=1:nokey=1",fs_path],
                    capture_output=True, text=True, timeout=30)
                if probe.returncode != 0 or not probe.stdout.strip():
                    return self.send_error(404)
                try: dur = float(probe.stdout.strip())
                except ValueError: dur = 0.0
                seek = min(max(dur/2.0, 0.0), 60.0)
                gen = subprocess.run(
                    ["ffmpeg","-y","-ss",f"{seek:.2f}","-i",fs_path,
                     "-frames:v","1","-vf",f"scale=-2:{THUMB_HEIGHT}",
                     "-q:v",str(THUMB_QUALITY),"-f","image2",out],
                    capture_output=True, timeout=60)
                if gen.returncode != 0 or not os.path.exists(out):
                    try: os.remove(out)
                    except OSError: pass
                    return self.send_error(404)
            with open(out,"rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type","image/jpeg")
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","public, max-age=604800")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers(); self.wfile.write(body)
        except (OSError, subprocess.SubprocessError, TimeoutError):
            return self.send_error(404)

    def _is_admin(self):
        if not self.auth_user: return True
        auth = self.headers.get("Authorization","")
        if auth.startswith("Basic "):
            try:
                u,p = base64.b64decode(auth.split(None,1)[1]).decode().split(":",1)
                if u==self.auth_user and p==self.auth_pass: return True
            except Exception: pass
        token = self._get_session_token()
        return bool(token and validate_session(token))

    def _endpoint(self, path):
        idx = path.rfind("/_api/")
        if idx != -1:
            return "/_api/" + path[idx + len("/_api/"):]
        if path == "/_login" or path.startswith("/_login/") or path.endswith("/_login"):
            return "/_login"
        return path

    def do_GET(self):
        if self._enforce_https(): return
        raw_path, _, raw_query = self.path.partition("?")
        path = urllib.parse.unquote(raw_path)
        qs = urllib.parse.parse_qs(raw_query)
        ep = self._endpoint(path)

        if ep == "/_login":
            return self._html(LOGIN_HTML)
        if ep == "/_api/zip-dl":
            if not self._check_auth(): return
            key = qs.get("key", [""])[0]
            if not key: return self._json({"error": "Missing key"}, 400)
            return self._serve_zip(key)

        if not self._check_auth(): return

        if ep == "/_api/list":
            dirs_only = qs.get("dirs", ["0"])[0].lower() in ("1","true","yes")
            return self._api_list(qs.get("path", ["/"])[0], dirs_only)
        if ep == "/_api/search":
            return self._api_search(qs.get("q", [""])[0], qs.get("path", ["/"])[0])
        if ep == "/_api/disk":
            return self._json(disk_info(self.base_dir))

        fs_path = path
        if "/_ui" in path:
            fs_path = "/" + path.split("/_ui", 1)[1].lstrip("/")

        fs = self._resolve(fs_path)
        if not fs or not os.path.exists(fs):
            # If path doesn't resolve to a file in base_dir, serve UI_HTML SPA
            html = UI_HTML.replace("__IS_ADMIN__", "true" if self._is_admin() else "false"
                          ).replace("__MAX_UPLOAD__", str(self.max_upload))
            return self._html(html)

        if os.path.isdir(fs):
            if not fs_path.endswith("/"):
                self.send_response(301)
                loc = fs_path + "/"
                if raw_query: loc += "?" + raw_query
                self.send_header("Location", loc)
                self.end_headers()
                return
            html = UI_HTML.replace("__IS_ADMIN__", "true" if self._is_admin() else "false"
                          ).replace("__MAX_UPLOAD__", str(self.max_upload))
            return self._html(html)

        if os.path.isfile(fs):
            if qs.get("thumb") and self._is_video(fs):
                return self._serve_thumb(fs)
            return self._serve_file(fs)

        self.send_error(404)

    def do_HEAD(self):
        if self._enforce_https(): return
        if not self._check_auth(): return
        fs = self._resolve(urllib.parse.unquote(self.path.split("?", 1)[0]))
        if not fs: return self.send_error(403)
        if os.path.isfile(fs): return self._serve_file(fs,head_only=True)
        if os.path.isdir(fs):
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length","0")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            return
        self.send_error(404)

    def do_PUT(self):
        if not self._check_auth(require_admin=True): return
        length = int(self.headers.get("Content-Length",0))
        crange = self.headers.get("Content-Range"); start_byte=0; total_size=length
        if crange and crange.startswith("bytes "):
            try: rng,tot=crange[6:].split("/"); start_byte=int(rng.split("-")[0]); total_size=int(tot)
            except Exception: pass
        if total_size > self.max_upload:
            self.send_error(413,f"Max upload: {human_size(self.max_upload)}")
            rem=length
            while rem>0:
                chunk=self.rfile.read(min(CHUNK,rem))
                if not chunk: break
                rem -= len(chunk)
            return
        di = disk_info(self.base_dir)
        if total_size > di["free"] - 100 * 1024 * 1024: return self.send_error(507,"Not enough disk space")
        fs = self._resolve(urllib.parse.unquote(self.path.split("?", 1)[0]))
        if not fs or fs==os.path.realpath(self.base_dir): return self.send_error(403)
        os.makedirs(os.path.dirname(fs),exist_ok=True)
        mode = "r+b" if start_byte>0 and os.path.exists(fs) else "wb"
        try:
            with open(fs,mode) as f:
                if start_byte>0: f.seek(start_byte)
                rem=length
                while rem>0:
                    chunk=self.rfile.read(min(CHUNK,rem))
                    if not chunk: break
                    f.write(chunk); rem -= len(chunk)
            if total_size and start_byte + length >= total_size:
                if os.path.getsize(fs) != total_size:
                    return self.send_error(400,"Upload size mismatch")
            self._text("Uploaded\n",201)
        except OSError as e: self.send_error(500,str(e))

    def do_POST(self):
        path = urllib.parse.unquote(self.path.split("?", 1)[0])
        ep = self._endpoint(path)

        if ep == "/_api/login":
            return self._api_login()
        if not self._check_auth(): return
        if ep == "/_api/logout":
            return self._api_logout()
        if ep == "/_api/zip":
            return self._api_zip_prepare()

        if not self._check_auth(require_admin=True): return

        if ep == "/_api/delete":
            return self._api_delete()
        if ep == "/_api/rename":
            return self._api_rename()
        if ep == "/_api/mkdir":
            return self._api_mkdir()

        self.send_error(404, "Unknown endpoint")

    def do_DELETE(self):
        if not self._check_auth(require_admin=True): return
        fs = self._resolve(urllib.parse.unquote(self.path.split("?", 1)[0]))
        if not fs or fs==os.path.realpath(self.base_dir): return self.send_error(403)
        if not os.path.exists(fs): return self.send_error(404)
        try:
            if os.path.isdir(fs): shutil.rmtree(fs)
            else: os.remove(fs)
            self._text("Deleted\n")
        except OSError as e: self.send_error(500,str(e))


def parse_size(s):
    s = s.strip().upper()
    if not s: return 0
    for suffix,mult in [("TB",1024**4),("GB",1024**3),("MB",1024**2),("KB",1024),
                         ("T",1024**4),("G",1024**3),("M",1024**2),("K",1024),("B",1)]:
        if s.endswith(suffix): return int(float(s[:-len(suffix)])*mult)
    try:
        return int(float(s)*1024**3)
    except ValueError:
        return 0

class BoundedHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sem = threading.BoundedSemaphore(MAX_CONN)
    def process_request(self, request, client_address):
        if not self._sem.acquire(blocking=False):
            try:
                request.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
                request.close()
            except OSError:
                pass
            return
        threading.Thread(target=self.process_request_thread, args=(request, client_address), daemon=True).start()
    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._sem.release()

class SecureHTTPServer(BoundedHTTPServer):
    def __init__(self,server_address,RequestHandlerClass,ssl_context):
        super().__init__(server_address,RequestHandlerClass); self.ssl_context=ssl_context
    def process_request_thread(self,request,client_address):
        try:
            request.settimeout(10.0); request=self.ssl_context.wrap_socket(request,server_side=True)
            request.settimeout(None)
        except Exception:
            try: request.close()
            except Exception: pass
            self._sem.release()
            return
        BoundedHTTPServer.process_request_thread(self, request, client_address)

def main():
    p = argparse.ArgumentParser(description="FileStation v3.1")
    p.add_argument("-p","--port",type=int,default=80)
    p.add_argument("--https-port",type=int,default=443)
    p.add_argument("-d","--directory",default=os.getcwd())
    p.add_argument("-u","--user",default=os.environ.get("FS_USER","admin"))
    p.add_argument("--password",default=os.environ.get("FS_PASS","secret"))
    p.add_argument("--public",action="store_true")
    p.add_argument("--no-https",action="store_true")
    p.add_argument("--no-http",action="store_true")
    p.add_argument("--force-https",action="store_true")
    p.add_argument("--cert")
    p.add_argument("--key")
    p.add_argument("--max-upload",default="10G")
    p.add_argument("--nginx-prefix",default=os.environ.get("FS_NGINX_PREFIX",""))
    p.add_argument("--thumb-dir",default=THUMB_DIR)
    args = p.parse_args()
    Handler.base_dir=os.path.realpath(args.directory); Handler.auth_user=args.user
    Handler.auth_pass=args.password; Handler.max_upload=parse_size(args.max_upload)
    Handler.public_mode=args.public; Handler.force_https=args.force_https; Handler.https_port=args.https_port; Handler.nginx_accel_prefix=args.nginx_prefix
    Handler.thumb_dir = os.path.realpath(args.thumb_dir)
    print(f"\n  {BLD}FileStation v{VERSION}{RST}")
    print(f"  {'─'*42}")
    print(f"  Directory:  {Handler.base_dir}")
    print(f"  Auth:       {args.user}:{'*'*len(args.password)}")
    print(f"  Max upload: {human_size(Handler.max_upload)}\n")
    servers=[]
    if not args.no_http:
        srv=BoundedHTTPServer(("0.0.0.0",args.port),Handler)
        print(f"  HTTP  -> http://0.0.0.0:{args.port}/")
        threading.Thread(target=srv.serve_forever,daemon=True).start(); servers.append(srv)
    if not args.no_https:
        if not args.cert or not args.key:
            print("  HTTPS disabled: pass --cert and --key to enable HTTPS (no self-signed certs are generated)")
        else:
            try:
                ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(args.cert,args.key)
                srv=SecureHTTPServer(("0.0.0.0",args.https_port),Handler,ctx)
                print(f"  HTTPS -> https://0.0.0.0:{args.https_port}/")
                threading.Thread(target=srv.serve_forever,daemon=True).start(); servers.append(srv)
            except (ssl.SSLError, OSError) as e:
                print(f"  HTTPS disabled: could not load cert/key ({e})")
    print(f"\n  Press Ctrl+C to stop\n")
    try: threading.Event().wait()
    except KeyboardInterrupt:
        print(f"\n  Shutting down...")
        for s in servers: s.shutdown()
        print(f"  Stopped.\n")

if __name__ == "__main__":
    main()
