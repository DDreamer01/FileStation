UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FileStation</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📂</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#09090b;--surface:#18181b;--surface2:#27272a;--border:#3f3f46;
  --text:#fafafa;--text2:#a1a1aa;--accent:#8b5cf6;--accent-hover:#7c3aed;
  --success:#22c55e;--error:#ef4444;--warn:#eab308;
  --radius:8px;--radius-lg:12px;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
.markdown-body h1 { font-size: 2em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }
.markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }
.markdown-body p, .markdown-body blockquote, .markdown-body ul, .markdown-body ol { margin-top: 0; margin-bottom: 16px; }
.markdown-body a { color: var(--accent); }
.markdown-body code { background: rgba(240,246,252,0.15); padding: .2em .4em; border-radius: 6px; font-family: monospace; font-size: 85%; }
.markdown-body pre { background: #161b22; padding: 16px; border-radius: 6px; overflow: auto; }
.markdown-body pre code { background: transparent; padding: 0; }
.markdown-body blockquote { padding: 0 1em; color: var(--text2); border-left: .25em solid var(--border); }
.markdown-body img { max-width: 100%; box-sizing: content-box; background-color: var(--bg); }
html{font-family:'Inter',system-ui,sans-serif;font-size:14px;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}
body{min-height:100vh;overflow-x:hidden}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#52525b}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer;border:none;background:none;color:inherit;font-size:inherit}
input{font-family:inherit;font-size:inherit}

/* Header */
.header{
  position:sticky;top:0;z-index:100;
  background:rgba(24,24,27,0.75);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
  padding:12px 24px;
  display:flex;align-items:center;gap:16px;flex-wrap:wrap;
}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:18px;flex-shrink:0;white-space:nowrap}
.logo svg{width:28px;height:28px}
.breadcrumbs{display:flex;align-items:center;gap:4px;flex:1;min-width:0;overflow-x:auto;white-space:nowrap;scrollbar-width:none}
.breadcrumbs::-webkit-scrollbar{display:none}
.crumb{color:var(--text2);padding:4px 6px;border-radius:4px;transition:all .15s;font-size:13px;cursor:pointer}
.crumb:hover{color:var(--text);background:var(--surface2)}
.crumb-sep{color:var(--border);font-size:12px;user-select:none}
.crumb:last-child{color:var(--text);font-weight:500}
.search-box{
  position:relative;flex-shrink:0;width:240px;
}
.search-box input{
  width:100%;padding:8px 12px 8px 34px;
  background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);
  color:var(--text);outline:none;transition:border-color .15s;
}
.search-box input:focus{border-color:var(--accent)}
.search-box input::placeholder{color:var(--text2)}
.search-box svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--text2);pointer-events:none}
.disk-usage{display:flex;align-items:center;gap:8px;flex-shrink:0;font-size:12px;color:var(--text2)}
.disk-bar{width:80px;height:6px;background:var(--surface2);border-radius:3px;overflow:hidden}
.disk-fill{height:100%;background:var(--accent);border-radius:3px;transition:width .3s}
.disk-fill.warn{background:var(--warn)}
.disk-fill.danger{background:var(--error)}

/* Toolbar */
.toolbar{
  display:flex;align-items:center;gap:8px;padding:8px 24px;
  border-bottom:1px solid var(--border);background:var(--surface);
  flex-wrap:wrap;
}
.toolbar-left{display:flex;align-items:center;gap:8px;flex:1}
.toolbar-right{display:flex;align-items:center;gap:8px}
.btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:7px 14px;border-radius:var(--radius);font-size:13px;font-weight:500;
  transition:all .15s;white-space:nowrap;
}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent-hover)}
.btn-danger{background:var(--error);color:#fff}
.btn-danger:hover{background:#dc2626}
.btn-ghost{color:var(--text2);background:transparent}
.btn-ghost:hover{background:var(--surface2);color:var(--text)}
.btn-outline{border:1px solid var(--border);color:var(--text2)}
.btn-outline:hover{border-color:var(--text2);color:var(--text)}
.btn svg{width:16px;height:16px}
.bulk-actions{
  display:none;align-items:center;gap:8px;
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:200;
  background:rgba(24,24,27,0.95);backdrop-filter:blur(8px);
  padding:8px 16px;border:1px solid var(--border);border-radius:24px;
  box-shadow:0 8px 32px rgba(0,0,0,0.5);
  animation:slideUp .2s ease;
}
.bulk-actions.show{display:flex}
.selected-count{font-size:13px;font-weight:500;color:var(--text);margin-right:8px}

/* Sort header */
.sort-header{
  display:grid;grid-template-columns:40px 1fr 100px 160px 100px;
  padding:6px 24px;border-bottom:1px solid var(--border);
  background:var(--bg);font-size:12px;color:var(--text2);
  text-transform:uppercase;letter-spacing:.05em;font-weight:600;
  position:sticky;top:57px;z-index:50;
}
.sort-col{display:flex;align-items:center;gap:4px;cursor:pointer;padding:4px 0;user-select:none;transition:color .15s}
.sort-col:hover{color:var(--text)}
.sort-col.active{color:var(--accent)}
.sort-arrow{font-size:10px;opacity:0;transition:opacity .15s}
.sort-col.active .sort-arrow{opacity:1}
.sort-col:first-child{cursor:default}

/* File list */
.file-list{min-height:200px}
.file-row{
  display:grid;grid-template-columns:40px 1fr 100px 160px 100px;
  padding:4px 24px;border-bottom:1px solid rgba(63,63,70,0.3);
  align-items:center;transition:background .1s;cursor:default;
  animation:fadeIn .2s ease;
}
.file-row:hover{background:rgba(139,92,246,0.04)}
.file-row.selected{background:rgba(139,92,246,0.08)}
.file-name{display:flex;align-items:center;gap:10px;min-width:0}
.file-icon{font-size:20px;flex-shrink:0;width:28px;text-align:center;line-height:1}
.file-name-link{
  color:var(--text);font-weight:400;cursor:pointer;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  min-width:0;transition:color .15s;
}
.file-name-link:hover{color:var(--accent)}
.file-name-link.is-dir{font-weight:500}
.file-search-path{font-size:11px;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-name-wrap{min-width:0;overflow:hidden}
.file-size,.file-date{color:var(--text2);font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-actions{display:flex;gap:2px;opacity:0;transition:opacity .15s;justify-content:flex-end}
.file-row:hover .file-actions{opacity:1}
.action-btn{
  padding:6px;border-radius:6px;color:var(--text2);
  display:inline-flex;align-items:center;justify-content:center;transition:all .15s;
}
.action-btn:hover{background:var(--surface2);color:var(--text)}
.action-btn.action-delete:hover{color:var(--error)}
.action-btn svg{width:16px;height:16px}

/* Checkbox */
.cb{
  position:relative;width:18px;height:18px;
  appearance:none;-webkit-appearance:none;
  background:var(--surface2);border:1.5px solid var(--border);border-radius:4px;
  cursor:pointer;transition:all .15s;flex-shrink:0;
}
.cb:checked{background:var(--accent);border-color:var(--accent)}
.cb:checked::after{
  content:'';position:absolute;left:5px;top:2px;
  width:5px;height:9px;
  border:solid #fff;border-width:0 2px 2px 0;
  transform:rotate(45deg);
}
.cb:hover{border-color:var(--text2)}

/* Empty state */
.empty-state{
  display:none;flex-direction:column;align-items:center;justify-content:center;
  padding:80px 20px;color:var(--text2);gap:12px;
  animation:fadeIn .3s ease;
}
.empty-state.show{display:flex}
.empty-state .emoji{font-size:64px;opacity:0.4}
.empty-state .msg{font-size:15px}
.empty-state .sub{font-size:13px;color:var(--border)}

/* Drop overlay */
.drop-overlay{
  display:none;position:fixed;inset:0;z-index:9999;
  background:rgba(9,9,11,0.85);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  flex-direction:column;align-items:center;justify-content:center;gap:16px;
  border:3px dashed var(--accent);margin:16px;border-radius:var(--radius-lg);
}
.drop-overlay.show{display:flex}
.drop-overlay .emoji{font-size:72px;animation:bounce 1s infinite}
.drop-overlay .label{font-size:20px;font-weight:600;color:var(--accent)}

/* Upload panel */
.upload-panel{
  display:none;position:fixed;bottom:20px;right:20px;z-index:200;
  width:360px;max-height:400px;
  background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);
  box-shadow:0 8px 32px rgba(0,0,0,0.5);
  animation:slideUp .25s ease;overflow:hidden;
}
.upload-panel.show{display:block}
.upload-panel-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;border-bottom:1px solid var(--border);font-weight:600;font-size:13px;
}
.upload-panel-close{
  width:28px;height:28px;display:flex;align-items:center;justify-content:center;
  border-radius:6px;color:var(--text2);transition:all .15s;font-size:18px;
}
.upload-panel-close:hover{background:var(--surface2);color:var(--text)}
.upload-panel-body{overflow-y:auto;max-height:320px;padding:8px 0}
.upload-item{padding:8px 16px;display:flex;flex-direction:column;gap:4px}
.upload-item-header{display:flex;justify-content:space-between;align-items:center}
.upload-item-name{font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px}
.upload-item-pct{font-size:11px;color:var(--text2);flex-shrink:0}
.upload-progress-track{width:100%;height:4px;background:var(--surface2);border-radius:2px;overflow:hidden}
.upload-progress-fill{height:100%;background:var(--accent);border-radius:2px;transition:width .15s;width:0%}
.upload-progress-fill.done{background:var(--success)}
.upload-progress-fill.err{background:var(--error)}

/* Toast */
.toast-container{
  position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:9000;
  display:flex;flex-direction:column-reverse;gap:8px;align-items:center;pointer-events:none;
}
.toast{
  padding:10px 20px;border-radius:var(--radius);font-size:13px;font-weight:500;
  pointer-events:auto;animation:toastIn .25s ease;
  box-shadow:0 4px 16px rgba(0,0,0,0.4);max-width:400px;text-align:center;
}
.toast.success{background:var(--success);color:#fff}
.toast.error{background:var(--error);color:#fff}
.toast.info{background:var(--surface2);color:var(--text);border:1px solid var(--border)}
.toast.out{animation:toastOut .2s ease forwards}

/* Modal */
.modal-backdrop{
  display:none;position:fixed;inset:0;z-index:500;
  background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);
  align-items:center;justify-content:center;
}
.modal-backdrop.show{display:flex}
.modal{
  background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);
  padding:24px;width:90%;max-width:420px;animation:modalIn .2s ease;
  box-shadow:0 16px 48px rgba(0,0,0,0.5);
}
.modal h3{font-size:16px;font-weight:600;margin-bottom:8px}
.modal p{font-size:13px;color:var(--text2);margin-bottom:16px;line-height:1.6}
.modal input[type="text"]{
  width:100%;padding:10px 12px;background:var(--surface2);
  border:1px solid var(--border);border-radius:var(--radius);
  color:var(--text);outline:none;margin-bottom:16px;transition:border-color .15s;
}
.modal input[type="text"]:focus{border-color:var(--accent)}
.modal-actions{display:flex;gap:8px;justify-content:flex-end}
.modal .delete-list{
  max-height:120px;overflow-y:auto;background:var(--surface2);
  border-radius:var(--radius);padding:8px 12px;margin-bottom:16px;
  font-size:12px;color:var(--text2);
}
.modal .delete-list div{padding:2px 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* Preview */
.preview-overlay{
  display:none;position:fixed;inset:0;z-index:600;
  background:rgba(0,0,0,0.92);
  flex-direction:column;animation:fadeIn .2s ease;
}
.preview-overlay.show{display:flex}
.preview-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 20px;border-bottom:1px solid var(--border);flex-shrink:0;
  background:rgba(24,24,27,0.8);backdrop-filter:blur(8px);
}
.preview-title{font-size:14px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;margin:0 16px}
.preview-body{flex:1;display:flex;align-items:center;justify-content:center;overflow:auto;padding:20px}
.preview-body img{max-width:100%;max-height:100%;object-fit:contain;border-radius:4px}
.preview-body video{max-width:100%;max-height:100%;border-radius:4px}
.preview-body audio{width:320px}
.preview-body iframe{width:100%;height:100%;border:none;border-radius:4px;background:#fff}
.preview-body pre{
  background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:20px;max-width:900px;width:100%;max-height:100%;overflow:auto;
  font-family:'JetBrains Mono','Fira Code',monospace;font-size:13px;
  white-space:pre-wrap;word-break:break-word;color:var(--text2);
}

/* Context menu */
.ctx-menu{
  position:fixed;z-index:400;
  background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  box-shadow:0 8px 24px rgba(0,0,0,0.4);
  min-width:160px;padding:4px;animation:ctxIn .12s ease;overflow:hidden;
}
.ctx-item{
  display:flex;align-items:center;gap:8px;
  padding:8px 12px;border-radius:6px;font-size:13px;cursor:pointer;
  transition:background .1s;
}
.ctx-item:hover{background:var(--surface2)}
.ctx-item.danger{color:var(--error)}
.ctx-item .ci{width:18px;text-align:center;font-size:14px}

/* Skeleton */
.skeleton-row{
  display:grid;grid-template-columns:40px 1fr 100px 160px 100px;
  padding:10px 24px;gap:8px;align-items:center;
}
.skeleton-block{
  height:14px;border-radius:4px;
  background:linear-gradient(90deg,var(--surface2) 25%,var(--border) 50%,var(--surface2) 75%);
  background-size:200% 100%;
  animation:shimmer 1.5s infinite;
}
.skeleton-cb{width:18px;height:18px;border-radius:4px;background:var(--surface2)}
.skeleton-name{width:60%}
.skeleton-size{width:50px}
.skeleton-date{width:100px}
.skeleton-act{width:60px}

/* Animations */
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
@keyframes toastIn{from{opacity:0;transform:translateY(12px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes toastOut{from{opacity:1;transform:translateY(0) scale(1)}to{opacity:0;transform:translateY(12px) scale(.9)}}
@keyframes modalIn{from{opacity:0;transform:scale(.95) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes ctxIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}

/* Responsive */
@media(max-width:768px){
  .header{padding:10px 14px;gap:10px}
  .search-box{width:100%;order:10}
  .disk-usage{display:none}
  .sort-header{grid-template-columns:36px 1fr auto;padding:6px 14px}
  .sort-col-size,.sort-col-date{display:none}
  .file-row{grid-template-columns:36px 1fr auto;padding:4px 14px}
  .file-size,.file-date{display:none}
  .file-actions{opacity:1}
  .toolbar{padding:8px 14px}
  .skeleton-row{grid-template-columns:36px 1fr auto}
  .skeleton-size,.skeleton-date{display:none}
  .upload-panel{width:calc(100% - 20px);right:10px;bottom:10px}
}
@media(max-width:480px){
  .logo span{display:none}
}

.filter-group { display: flex; gap: 8px; align-items: center; }
.filter-select {
  background: var(--surface2); border: 1px solid var(--border); color: var(--text);
  padding: 6px 10px; border-radius: 6px; font-size: 12px; font-family: inherit;
  outline: none; cursor: pointer; transition: border-color .15s;
}
.filter-select:focus { border-color: var(--accent); }
.logout-btn {
  background: none; border: none; color: var(--text2); font-size: 18px;
  cursor: pointer; padding: 6px; border-radius: 6px; transition: all .15s;
  display: flex; align-items: center; justify-content: center;
}
.logout-btn:hover { color: var(--error); background: rgba(239, 68, 68, 0.1); }
.file-children { font-size: 11px; color: var(--text2); margin-left: 6px; }
.admin-only { display: none !important; }
body.is-admin .admin-only { display: flex !important; }
body.is-admin .admin-only-block { display: block !important; }
body.is-admin .admin-only-inline { display: inline-block !important; }

</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <a class="logo" href="/" style="text-decoration:none;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--accent)">
      <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
    </svg>
    <span>FileStation</span>
  </a>
  <nav class="breadcrumbs" id="breadcrumbs"></nav>
  <div class="search-box">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" id="searchInput" placeholder="Search files..." autocomplete="off">
  </div>
  <div class="disk-usage" id="diskUsage"></div>
  <button class="logout-btn admin-only" id="logoutBtn" title="Logout">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
  </button>
</header>

<div class="toolbar">
  <div class="toolbar-left" style="flex-wrap:wrap;">
    <input type="checkbox" class="cb" id="selectAll" title="Select all">
    <div class="filter-group">
      <select class="filter-select" id="filterSize">
        <option value="0">All sizes</option>
        <option value="1024">&ge; 1 KB</option>
        <option value="1048576">&ge; 1 MB</option>
        <option value="10485760">&ge; 10 MB</option>
        <option value="104857600">&ge; 100 MB</option>
        <option value="1073741824">&ge; 1 GB</option>
      </select>
      <select class="filter-select" id="filterDate">
        <option value="">All dates</option>
        <option value="today">Today</option>
        <option value="week">This week</option>
        <option value="month">This month</option>
        <option value="year">This year</option>
      </select>
      <label class="admin-only" style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer">
        <input type="checkbox" class="cb" id="showHidden"> Hidden
      </label>
    </div>
    <div class="bulk-actions" id="bulkActions">
      <span class="selected-count" id="selectedCount"></span>
      <button class="btn btn-outline" id="bulkDownloadBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download
      </button>
      <button class="btn btn-danger admin-only" id="bulkDeleteBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
        Delete
      </button>
    </div>
  </div>
  <div class="toolbar-right">
    <button class="btn btn-outline admin-only" id="newFolderBtn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
      New Folder
    </button>
    <button class="btn btn-primary admin-only" id="uploadBtn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      Upload
    </button>
  </div>
</div>
<input type="file" id="fileInput" multiple hidden>

<!-- Sort header -->
<div class="sort-header" id="sortHeader">
  <div class="sort-col">&nbsp;</div>
  <div class="sort-col active" data-sort="name">Name <span class="sort-arrow">&#9650;</span></div>
  <div class="sort-col sort-col-size" data-sort="size">Size <span class="sort-arrow">&#9650;</span></div>
  <div class="sort-col sort-col-date" data-sort="modified">Modified <span class="sort-arrow">&#9650;</span></div>
  <div class="sort-col">Actions</div>
</div>

<!-- File list -->
<div class="file-list" id="fileList"></div>

<!-- Empty state -->
<div class="empty-state" id="emptyState">
  <div class="emoji">📂</div>
  <div class="msg">This folder is empty</div>
  <div class="sub">Drop files here or click Upload</div>
</div>

<!-- Drop overlay -->
<div class="drop-overlay" id="dropOverlay">
  <div class="emoji">📥</div>
  <div class="label">Drop files to upload</div>
</div>

<!-- Upload panel -->
<div class="upload-panel" id="uploadPanel">
  <div class="upload-panel-header">
    <span>Uploads</span>
    <button class="upload-panel-close" id="uploadPanelClose">&times;</button>
  </div>
  <div class="upload-panel-body" id="uploadPanelBody"></div>
</div>

<!-- Toast container -->
<div class="toast-container" id="toastContainer"></div>

<!-- Modal backdrop (reusable) -->
<div class="modal-backdrop" id="modalBackdrop">
  <div class="modal" id="modalContent"></div>
</div>

<!-- Preview overlay -->
<div class="preview-overlay" id="previewOverlay">
  <div class="preview-header">
    <button class="btn btn-ghost" id="previewClose">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <div class="preview-title" id="previewTitle"></div>
    <a class="btn btn-outline" id="previewDownload" download>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download
    </a>
  </div>
  <div class="preview-body" id="previewBody"></div>
</div>
<footer style="text-align:center; padding:24px; font-size:12px; color:var(--text2); opacity: 0.7;">
  Developed by &dagger;h&epsilon; dr&epsilon;&alpha;m&epsilon;r
</footer>

<script>
(function(){
  var MAX_UPLOAD = __MAX_UPLOAD__;

  var currentPath = decodeURIComponent(window.location.pathname);
  if (currentPath.charAt(currentPath.length - 1) !== "/") currentPath += "/";

  var entries = [];
  var selected = new Set();
  var sortKey = "name";
  var sortAsc = true;
  var dragCount = 0;
  var searchTimer = null;
  var isSearching = false;
  var IS_ADMIN = __IS_ADMIN__;
  var showDotfiles = false;
  var filterSize = 0;
  var filterDate = "";

  if (IS_ADMIN) document.body.classList.add("is-admin");

  var $ = function(id){ return document.getElementById(id); };

  function init(){
    loadDirectory();
    setupEvents();
  }

  async function api(url, opts){
    opts = opts || {};
    opts.credentials = "same-origin";
    var resp = await fetch(url, opts);
    var data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Request failed");
    return data;
  }

  async function loadDirectory(){
    var fl = $("fileList");
    fl.innerHTML = skeletonHTML();
    $("emptyState").classList.remove("show");
    selected.clear();
    updateBulkUI();
    try {
      var data = await api("/_api/list?path=" + encodeURIComponent(currentPath));
      entries = data.entries || [];
      if (data.disk) renderDisk(data.disk);
      renderBreadcrumbs();
      renderEntries();
    } catch(e){
      fl.innerHTML = "";
      toast(e.message, "error");
    }
  }

  function skeletonHTML(){
    var h = "";
    for (var i = 0; i < 8; i++){
      h += '<div class="skeleton-row">' +
        '<div class="skeleton-block skeleton-cb"></div>' +
        '<div class="skeleton-block skeleton-name"></div>' +
        '<div class="skeleton-block skeleton-size"></div>' +
        '<div class="skeleton-block skeleton-date"></div>' +
        '<div class="skeleton-block skeleton-act"></div>' +
        '</div>';
    }
    return h;
  }

  function renderBreadcrumbs(){
    var bc = $("breadcrumbs");
    var parts = currentPath.split("/").filter(Boolean);
    var html = '<span class="crumb" data-path="/">~</span>';
    var path = "/";
    for (var i = 0; i < parts.length; i++){
      path += parts[i] + "/";
      html += '<span class="crumb-sep">/</span>';
      html += '<span class="crumb" data-path="' + escapeAttr(path) + '">' + escapeHtml(decodeURIComponent(parts[i])) + '</span>';
    }
    bc.innerHTML = html;
  }

  function filterEntries(list) {
    var now = Date.now() / 1000;
    return list.filter(function(e) {
      if (!showDotfiles && e.name.charAt(0) === ".") return false;
      if (filterSize > 0 && e.type === "file" && (e.size || 0) < filterSize) return false;
      if (filterDate) {
        var cutoff = 0;
        if (filterDate === "today") cutoff = now - 86400;
        else if (filterDate === "week") cutoff = now - 604800;
        else if (filterDate === "month") cutoff = now - 2592000;
        else if (filterDate === "year") cutoff = now - 31536000;
        if (cutoff && (e.modified || 0) < cutoff) return false;
      }
      return true;
    });
  }

  function copyLink(name) {
    var url = window.location.origin + currentPath + encodeURIComponent(name);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function() { toast("Link copied!", "success"); });
    } else {
      var ta = document.createElement("textarea");
      ta.value = url;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      toast("Link copied!", "success");
    }
  }

  function downloadAsZip(paths, filename) {
    var dlBtn = $("bulkDownloadBtn");
    if(dlBtn) { dlBtn.disabled = true; dlBtn.innerHTML = "Zipping... 📦"; }
    toast("Zipping... Download will start automatically.", "info");
    api("/_api/zip", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({paths: paths})
    }).then(function(data) {
      window.location.href = "/_api/zip-dl?key=" + data.key;
      toast("Download started!", "success");
      if(dlBtn) { dlBtn.disabled = false; dlBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download'; }
    }).catch(function(e) {
      toast(e.message, "error");
      if(dlBtn) { dlBtn.disabled = false; dlBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download'; }
    });
  }

  function bulkDownload() {
    if (!selected.size) return;
    var paths = [];
    selected.forEach(function(n) { paths.push(currentPath + n); });
    downloadAsZip(paths, "download.zip");
  }

  function downloadFolderZip(name) {
    downloadAsZip([currentPath + name], name + ".zip");
  }

  function logout() {
    api("/_api/logout", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: "{}"
    }).then(function() {
      window.location.href = "/_login";
    }).catch(function() {
      window.location.href = "/_login";
    });
  }

  function renderDisk(disk){
    var du = $("diskUsage");
    if (!disk || !disk.total) { du.innerHTML = ""; return; }
    var pct = Math.round((disk.used / disk.total) * 100);
    var cls = "";
    if (pct > 90) cls = " danger";
    else if (pct > 75) cls = " warn";
    du.innerHTML = '<span>' + formatSize(disk.used) + ' / ' + formatSize(disk.total) + '</span>' +
      '<div class="disk-bar"><div class="disk-fill' + cls + '" style="width:' + pct + '%"></div></div>';
  }

  function renderEntries(){
    var fl = $("fileList");
    var es = $("emptyState");
    var filtered = filterEntries(entries);
    var sorted = sortEntries(filtered);
    if (sorted.length === 0){
      fl.innerHTML = "";
      es.classList.add("show");
      return;
    }
    es.classList.remove("show");
    var html = "";
    for (var i = 0; i < sorted.length; i++){
      var e = sorted[i];
      var isDir = e.type === "dir";
      var name = e.name;
      var href = isDir ? encodeURI(currentPath + name + "/") : encodeURI(currentPath + name);
      var checked = selected.has(name) ? " checked" : "";
      var selClass = selected.has(name) ? " selected" : "";
      var searchPathHtml = "";
      if (isSearching && e.path){
        searchPathHtml = '<div class="file-search-path">' + escapeHtml(e.path) + '</div>';
      }
      var childrenHtml = "";
      if (isDir && e.children !== undefined) {
        childrenHtml = '<span class="file-children">(' + e.children + ' items)</span>';
      }
      var actionsHtml = '<button class="action-btn action-copy" data-name="' + escapeAttr(name) + '" title="Copy link">🔗</button>';
      if (isDir) {
        actionsHtml += '<button class="action-btn action-zip" data-name="' + escapeAttr(name) + '" title="Download ZIP">📦</button>';
      } else {
        actionsHtml += '<a class="action-btn action-download" href="' + escapeAttr(href) + '" download title="Download"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></a>';
      }
      if (IS_ADMIN) {
        actionsHtml += '<button class="action-btn action-rename" data-name="' + escapeAttr(name) + '" title="Rename"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>';
        actionsHtml += '<button class="action-btn action-delete" data-name="' + escapeAttr(name) + '" title="Delete"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg></button>';
      }
      var cbHtml = '<input type="checkbox" class="cb row-cb"' + checked + '>';
      html += '<div class="file-row' + selClass + '" data-name="' + escapeAttr(name) + '" data-type="' + (isDir ? "dir" : "file") + '">' +
        cbHtml +
        '<div class="file-name">' +
          '<span class="file-icon">' + fileIcon(e) + '</span>' +
          '<div class="file-name-wrap">' +
            '<a class="file-name-link' + (isDir ? " is-dir" : "") + '" href="' + escapeAttr(href) + '" data-name="' + escapeAttr(name) + '">' + escapeHtml(name) + '</a>' +
            childrenHtml +
            searchPathHtml +
          '</div>' +
        '</div>' +
        '<div class="file-size">' + (isDir ? "&mdash;" : formatSize(e.size)) + '</div>' +
        '<div class="file-date">' + (e.modified ? formatDate(e.modified) : "&mdash;") + '</div>' +
        '<div class="file-actions">' + actionsHtml + '</div>' +
        '</div>';
    }
    fl.innerHTML = html;
  }

  function sortEntries(list){
    var arr = list.slice();
    arr.sort(function(a, b){
      var aDir = a.type === "dir" ? 0 : 1;
      var bDir = b.type === "dir" ? 0 : 1;
      if (aDir !== bDir) return aDir - bDir;
      var av, bv;
      if (sortKey === "name"){
        av = (a.name || "").toLowerCase();
        bv = (b.name || "").toLowerCase();
        if (av < bv) return sortAsc ? -1 : 1;
        if (av > bv) return sortAsc ? 1 : -1;
        return 0;
      }
      if (sortKey === "size"){
        av = a.size || 0;
        bv = b.size || 0;
      } else if (sortKey === "modified"){
        av = a.modified || 0;
        bv = b.modified || 0;
      }
      return sortAsc ? av - bv : bv - av;
    });
    return arr;
  }

  function fileIcon(entry){
    if (entry.type === "dir") return "📁";
    var name = (entry.name || "").toLowerCase();
    var dot = name.lastIndexOf(".");
    var ext = dot >= 0 ? name.substring(dot) : "";
    if ([".jpg",".jpeg",".png",".gif",".svg",".webp",".avif",".bmp"].indexOf(ext) >= 0) return "🖼️";
    if ([".mp4",".mkv",".avi",".mov",".webm"].indexOf(ext) >= 0) return "🎬";
    if ([".mp3",".wav",".flac",".ogg",".aac"].indexOf(ext) >= 0) return "🎵";
    if (ext === ".pdf") return "📕";
    if ([".doc",".docx"].indexOf(ext) >= 0) return "📘";
    if ([".xls",".xlsx"].indexOf(ext) >= 0) return "📗";
    if ([".txt",".md",".log",".py",".js",".ts",".html",".css",".json",".sh",".c",".go",".rs",".java",".yml",".yaml",".toml",".xml",".cfg",".ini",".conf"].indexOf(ext) >= 0) return "📝";
    if ([".zip",".tar",".gz",".7z",".rar",".bz2",".xz"].indexOf(ext) >= 0) return "📦";
    if ([".pem",".key",".crt",".cer"].indexOf(ext) >= 0) return "🔑";
    return "📄";
  }

  function navigate(path){
    if (path.charAt(path.length - 1) !== "/") path += "/";
    currentPath = path;
    isSearching = false;
    $("searchInput").value = "";
    selected.clear();
    window.history.pushState({path: path}, "", path);
    loadDirectory();
  }

  function setSort(key){
    if (sortKey === key){
      sortAsc = !sortAsc;
    } else {
      sortKey = key;
      sortAsc = true;
    }
    var cols = $("sortHeader").querySelectorAll(".sort-col[data-sort]");
    for (var i = 0; i < cols.length; i++){
      var c = cols[i];
      var arrow = c.querySelector(".sort-arrow");
      if (c.getAttribute("data-sort") === sortKey){
        c.classList.add("active");
        arrow.innerHTML = sortAsc ? "&#9650;" : "&#9660;";
      } else {
        c.classList.remove("active");
      }
    }
    renderEntries();
  }

  function toggleSelect(name, checked){
    if (checked) selected.add(name);
    else selected.delete(name);
    updateBulkUI();
    var row = $("fileList").querySelector('.file-row[data-name="' + CSS.escape(name) + '"]');
    if (row) row.classList.toggle("selected", checked);
  }

  function toggleSelectAll(checked){
    selected.clear();
    if (checked){
      for (var i = 0; i < entries.length; i++) selected.add(entries[i].name);
    }
    updateBulkUI();
    var cbs = $("fileList").querySelectorAll(".row-cb");
    for (var j = 0; j < cbs.length; j++){
      cbs[j].checked = checked;
      cbs[j].closest(".file-row").classList.toggle("selected", checked);
    }
  }

  function updateBulkUI(){
    var ba = $("bulkActions");
    var sc = $("selectedCount");
    var sa = $("selectAll");
    if (selected.size > 0){
      ba.classList.add("show");
      sc.textContent = selected.size + " selected";
    } else {
      ba.classList.remove("show");
    }
    sa.checked = entries.length > 0 && selected.size === entries.length;
  }

  function triggerUpload(){
    $("fileInput").click();
  }

  function handleFiles(fileList){
    if (!fileList || fileList.length === 0) return;
    var items = [];
    for (var i = 0; i < fileList.length; i++){
      var f = fileList[i];
      if (MAX_UPLOAD > 0 && f.size > MAX_UPLOAD){
        toast(f.name + " exceeds max upload size (" + formatSize(MAX_UPLOAD) + ")", "error");
        continue;
      }
      items.push({file: f, name: f.name, filepath: f.filepath, progress: 0, status: "pending"});
    }
    if (items.length === 0) return;
    var panel = $("uploadPanel");
    var body = $("uploadPanelBody");
    panel.classList.add("show");
    for (var j = 0; j < items.length; j++){
      var id = "upload-" + Date.now() + "-" + j;
      items[j].id = id;
      body.innerHTML += '<div class="upload-item" id="' + id + '">' +
        '<div class="upload-item-header"><span class="upload-item-name">' + escapeHtml(items[j].name) + '</span><span class="upload-item-pct">0%</span></div>' +
        '<div class="upload-progress-track"><div class="upload-progress-fill"></div></div>' +
        '</div>';
    }
    uploadQueue(items, 0);
  }

  function uploadQueue(items, idx){
    if (idx >= items.length){
      loadDirectory();
      setTimeout(function(){
        $("uploadPanel").classList.remove("show");
        $("uploadPanelBody").innerHTML = "";
      }, 3000);
      return;
    }
    var item = items[idx];
    var el = $(item.id);
    var fill = el ? el.querySelector(".upload-progress-fill") : null;
    var pctEl = el ? el.querySelector(".upload-item-pct") : null;
    
    var CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks
    var file = item.file;
    var total = file.size;
    var offset = 0;
    var name = item.filepath || item.name;

    function uploadNextChunk() {
      var chunk = file.slice(offset, offset + CHUNK_SIZE);
      var xhr = new XMLHttpRequest();
      xhr.open("PUT", currentPath + encodeURIComponent(name).replace(/%2F/g, "/"), true);
      if (total > 0) {
        xhr.setRequestHeader("Content-Range", "bytes " + offset + "-" + (offset + chunk.size - 1) + "/" + total);
      }
      xhr.upload.onprogress = function(ev){
        if (ev.lengthComputable){
          var pct = total > 0 ? Math.round(((offset + ev.loaded) / total) * 100) : 100;
          if (fill) fill.style.width = pct + "%";
          if (pctEl) pctEl.textContent = pct + "%";
        }
      };
      xhr.onload = function(){
        if (xhr.status >= 200 && xhr.status < 300){
          offset += chunk.size;
          if (offset < total) {
            uploadNextChunk();
          } else {
            if (fill){ fill.style.width = "100%"; fill.classList.add("done"); }
            if (pctEl) pctEl.textContent = "Done";
            toast(name + " uploaded", "success");
            uploadQueue(items, idx + 1);
          }
        } else {
          if (fill){ fill.style.width = "100%"; fill.classList.add("err"); }
          if (pctEl) pctEl.textContent = "Error";
          toast("Failed to upload " + name, "error");
          uploadQueue(items, idx + 1);
        }
      };
      xhr.onerror = function(){
        if (fill){ fill.style.width = "100%"; fill.classList.add("err"); }
        if (pctEl) pctEl.textContent = "Error";
        toast("Failed to upload " + name, "error");
        uploadQueue(items, idx + 1);
      };
      xhr.send(chunk);
    }

    var checkXhr = new XMLHttpRequest();
    checkXhr.open("HEAD", currentPath + encodeURIComponent(name).replace(/%2F/g, "/"), true);
    checkXhr.onload = function() {
      if (checkXhr.status === 200) {
        var existingSize = parseInt(checkXhr.getResponseHeader("Content-Length"), 10);
        if (!isNaN(existingSize) && existingSize < total) offset = existingSize;
        else if (existingSize === total) {
           if (fill){ fill.style.width = "100%"; fill.classList.add("done"); }
           if (pctEl) pctEl.textContent = "Done";
           toast(name + " already exists", "info");
           uploadQueue(items, idx + 1);
           return;
        }
      }
      uploadNextChunk();
    };
    checkXhr.onerror = function() { uploadNextChunk(); };
    checkXhr.send();
  }

  function onSearch(query){
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(function(){
      if (!query.trim()){
        isSearching = false;
        loadDirectory();
        return;
      }
      isSearching = true;
      $("fileList").innerHTML = skeletonHTML();
      $("emptyState").classList.remove("show");
      api("/_api/search?q=" + encodeURIComponent(query) + "&path=" + encodeURIComponent(currentPath))
        .then(function(data){
          entries = data.results || [];
          renderEntries();
        })
        .catch(function(e){
          $("fileList").innerHTML = "";
          toast(e.message, "error");
        });
    }, 300);
  }

  function previewFile(name){
    var lower = name.toLowerCase();
    var dot = lower.lastIndexOf(".");
    var ext = dot >= 0 ? lower.substring(dot) : "";
    var url = currentPath + encodeURIComponent(name);
    var imgExts = [".jpg",".jpeg",".png",".gif",".svg",".webp",".avif",".bmp"];
    var vidExts = [".mp4",".webm",".ogg",".mov"];
    var audExts = [".mp3",".wav",".flac",".ogg",".aac"];
    var textExts = [".txt",".md",".log",".py",".js",".ts",".jsx",".tsx",".html",".css",".json",".sh",".bash",".c",".cpp",".h",".go",".rs",".java",".rb",".php",".yml",".yaml",".toml",".xml",".cfg",".ini",".conf",".env",".gitignore",".dockerfile",".makefile",".csv"];

    var body = $("previewBody");
    $("previewTitle").textContent = name;
    $("previewDownload").href = url;

    var previewUrl = url + "?preview=1";

    if (imgExts.indexOf(ext) >= 0){
      body.innerHTML = '<img src="' + escapeAttr(previewUrl) + '" alt="' + escapeAttr(name) + '">';
    } else if (vidExts.indexOf(ext) >= 0){
      body.innerHTML = '<video controls autoplay src="' + escapeAttr(previewUrl) + '"></video>';
    } else if (audExts.indexOf(ext) >= 0){
      body.innerHTML = '<audio controls src="' + escapeAttr(previewUrl) + '"></audio>';
    } else if (ext === ".pdf"){
      body.innerHTML = '<iframe src="' + escapeAttr(previewUrl) + '"></iframe>';
    } else if (textExts.indexOf(ext) >= 0 || (ext === "" && dot < 0)){
      body.innerHTML = '<pre>Loading...</pre>';
      fetch(previewUrl, {credentials: "same-origin", headers: {"Range": "bytes=0-1048575"}})
        .then(function(r){
          var truncated = r.status === 206;
          return r.text().then(function(t){ return {text: t, truncated: truncated}; });
        })
        .then(function(result){
          var t = result.text;
          if (result.truncated) t += "\\n\\n--- File truncated (showing first 1 MB). Download the full file. ---";
          
          if (ext === ".md" && window.marked) {
            body.innerHTML = '<div class="markdown-body" style="padding:24px;max-width:800px;margin:0 auto;line-height:1.6;">' + marked.parse(t) + '</div>';
          } else {
            var lang = ext.substring(1);
            if (!lang) lang = "plaintext";
            if (lang === "py") lang = "python";
            if (lang === "js") lang = "javascript";
            if (lang === "sh") lang = "bash";
            body.innerHTML = '<pre style="margin:0;height:100%;border-radius:0;"><code class="language-' + lang + '"></code></pre>';
            var codeEl = body.querySelector("code");
            codeEl.textContent = t;
            if (window.Prism) Prism.highlightElement(codeEl);
          }
        })
        .catch(function(){
          body.innerHTML = '<pre>Failed to load file</pre>';
        });
    } else {
      var a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      return;
    }
    $("previewOverlay").classList.add("show");
  }

  function closePreview(){
    var overlay = $("previewOverlay");
    overlay.classList.remove("show");
    var body = $("previewBody");
    var video = body.querySelector("video");
    var audio = body.querySelector("audio");
    if (video) video.pause();
    if (audio) audio.pause();
    body.innerHTML = "";
  }

  function confirmDelete(namesArray){
    var listHtml = "";
    for (var i = 0; i < namesArray.length; i++){
      listHtml += "<div>" + escapeHtml(namesArray[i]) + "</div>";
    }
    var mc = $("modalContent");
    mc.innerHTML = '<h3>Delete ' + (namesArray.length === 1 ? "item" : namesArray.length + " items") + '?</h3>' +
      '<p>This action cannot be undone.</p>' +
      '<div class="delete-list">' + listHtml + '</div>' +
      '<div class="modal-actions">' +
        '<button class="btn btn-ghost" id="modalCancel">Cancel</button>' +
        '<button class="btn btn-danger" id="modalConfirm">Delete</button>' +
      '</div>';
    $("modalBackdrop").classList.add("show");
    $("modalCancel").addEventListener("click", hideModal);
    $("modalConfirm").addEventListener("click", function(){
      hideModal();
      var paths = [];
      for (var j = 0; j < namesArray.length; j++){
        paths.push(currentPath + namesArray[j]);
      }
      api("/_api/delete", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({paths: paths})
      }).then(function(){
        toast("Deleted " + namesArray.length + " item(s)", "success");
        selected.clear();
        loadDirectory();
      }).catch(function(e){
        toast(e.message, "error");
      });
    });
  }

  function bulkDelete(){
    if (selected.size === 0) return;
    confirmDelete(Array.from(selected));
  }

  function showRename(name){
    var mc = $("modalContent");
    mc.innerHTML = '<h3>Rename</h3>' +
      '<input type="text" id="renameInput" value="' + escapeAttr(name) + '">' +
      '<div class="modal-actions">' +
        '<button class="btn btn-ghost" id="modalCancel">Cancel</button>' +
        '<button class="btn btn-primary" id="modalConfirm">Rename</button>' +
      '</div>';
    $("modalBackdrop").classList.add("show");
    var inp = $("renameInput");
    inp.focus();
    var dotPos = name.lastIndexOf(".");
    if (dotPos > 0){
      inp.setSelectionRange(0, dotPos);
    } else {
      inp.select();
    }
    function doRename(){
      var newName = inp.value.trim();
      if (!newName || newName === name){ hideModal(); return; }
      hideModal();
      api("/_api/rename", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({from: currentPath + name, to: currentPath + newName})
      }).then(function(){
        toast("Renamed to " + newName, "success");
        loadDirectory();
      }).catch(function(e){
        toast(e.message, "error");
      });
    }
    $("modalCancel").addEventListener("click", hideModal);
    $("modalConfirm").addEventListener("click", doRename);
    inp.addEventListener("keydown", function(ev){
      if (ev.key === "Enter") doRename();
      if (ev.key === "Escape") hideModal();
    });
  }

  function showNewFolder(){
    var mc = $("modalContent");
    mc.innerHTML = '<h3>New Folder</h3>' +
      '<input type="text" id="folderInput" placeholder="Folder name">' +
      '<div class="modal-actions">' +
        '<button class="btn btn-ghost" id="modalCancel">Cancel</button>' +
        '<button class="btn btn-primary" id="modalConfirm">Create</button>' +
      '</div>';
    $("modalBackdrop").classList.add("show");
    var inp = $("folderInput");
    inp.focus();
    function doCreate(){
      var name = inp.value.trim();
      if (!name){ hideModal(); return; }
      hideModal();
      api("/_api/mkdir", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({path: currentPath + name})
      }).then(function(){
        toast("Created folder: " + name, "success");
        loadDirectory();
      }).catch(function(e){
        toast(e.message, "error");
      });
    }
    $("modalCancel").addEventListener("click", hideModal);
    $("modalConfirm").addEventListener("click", doCreate);
    inp.addEventListener("keydown", function(ev){
      if (ev.key === "Enter") doCreate();
      if (ev.key === "Escape") hideModal();
    });
  }

  function hideModal(){
    $("modalBackdrop").classList.remove("show");
  }

  function showCtx(event, name){
    event.preventDefault();
    hideCtx();
    var row = event.target.closest(".file-row");
    var type = row ? row.getAttribute("data-type") : "file";
    var menu = document.createElement("div");
    menu.className = "ctx-menu";
    menu.id = "ctxMenu";
    var items = [];
    if (type === "dir"){
      items.push({icon: "📂", label: "Open", action: "open"});
      items.push({icon: "📦", label: "Download ZIP", action: "zip"});
      items.push({icon: "🔗", label: "Copy Link", action: "copy"});
      if (IS_ADMIN) {
        items.push({icon: "✏️", label: "Rename", action: "rename"});
        items.push({icon: "🗑️", label: "Delete", action: "delete", cls: "danger"});
      }
    } else {
      items.push({icon: "👁️", label: "Preview", action: "preview"});
      items.push({icon: "⬇️", label: "Download", action: "download"});
      items.push({icon: "🔗", label: "Copy Link", action: "copy"});
      if (IS_ADMIN) {
        items.push({icon: "✏️", label: "Rename", action: "rename"});
        items.push({icon: "🗑️", label: "Delete", action: "delete", cls: "danger"});
      }
    }
    var html = "";
    for (var i = 0; i < items.length; i++){
      var it = items[i];
      html += '<div class="ctx-item' + (it.cls ? " " + it.cls : "") + '" data-action="' + it.action + '" data-name="' + escapeAttr(name) + '">' +
        '<span class="ci">' + it.icon + '</span>' + escapeHtml(it.label) + '</div>';
    }
    menu.innerHTML = html;
    document.body.appendChild(menu);

    var x = event.clientX;
    var y = event.clientY;
    var mw = menu.offsetWidth;
    var mh = menu.offsetHeight;
    if (x + mw > window.innerWidth) x = window.innerWidth - mw - 8;
    if (y + mh > window.innerHeight) y = window.innerHeight - mh - 8;
    menu.style.left = x + "px";
    menu.style.top = y + "px";

    menu.addEventListener("click", function(ev){
      var ci = ev.target.closest(".ctx-item");
      if (!ci) return;
      var action = ci.getAttribute("data-action");
      var n = ci.getAttribute("data-name");
      hideCtx();
      if (action === "open") navigate(currentPath + n + "/");
      else if (action === "preview") previewFile(n);
      else if (action === "download"){
        var a = document.createElement("a");
        a.href = currentPath + encodeURIComponent(n);
        a.download = n;
        a.click();
      }
      else if (action === "rename") showRename(n);
      else if (action === "delete") confirmDelete([n]);
      else if (action === "copy") copyLink(n);
      else if (action === "zip") downloadFolderZip(n);
    });
  }

  function hideCtx(){
    var existing = document.getElementById("ctxMenu");
    if (existing) existing.remove();
  }

  function toast(msg, type){
    type = type || "info";
    var el = document.createElement("div");
    el.className = "toast " + type;
    el.textContent = msg;
    $("toastContainer").appendChild(el);
    setTimeout(function(){
      el.classList.add("out");
      setTimeout(function(){ el.remove(); }, 200);
    }, 3000);
  }

  function formatSize(bytes){
    if (bytes == null) return "";
    if (bytes === 0) return "0 B";
    var units = ["B","KB","MB","GB","TB"];
    var i = 0;
    var b = bytes;
    while (b >= 1024 && i < units.length - 1){ b /= 1024; i++; }
    return (i === 0 ? b : b.toFixed(1)) + " " + units[i];
  }

  function formatDate(timestamp){
    var d = new Date(timestamp * 1000);
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var yesterday = new Date(today.getTime() - 86400000);
    var hh = String(d.getHours()).padStart(2, "0");
    var mm = String(d.getMinutes()).padStart(2, "0");
    var time = hh + ":" + mm;
    if (d >= today) return "Today " + time;
    if (d >= yesterday) return "Yesterday " + time;
    var months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    return months[d.getMonth()] + " " + d.getDate() + " " + time;
  }

  function escapeHtml(s){
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function escapeAttr(s){
    return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function setupEvents(){
    /* File input */
    $("fileInput").addEventListener("change", function(){
      handleFiles(this.files);
      this.value = "";
    });

    /* Search */
    $("searchInput").addEventListener("input", function(){
      onSearch(this.value);
    });

    /* Select all */
    $("selectAll").addEventListener("change", function(){
      toggleSelectAll(this.checked);
    });

    /* Buttons */
    $("uploadBtn").addEventListener("click", triggerUpload);
    $("newFolderBtn").addEventListener("click", showNewFolder);
    $("bulkDeleteBtn").addEventListener("click", bulkDelete);
    $("uploadPanelClose").addEventListener("click", function(){
      $("uploadPanel").classList.remove("show");
      $("uploadPanelBody").innerHTML = "";
    });

    /* v2: Filter controls */
    $("filterSize").addEventListener("change", function(){ filterSize = parseInt(this.value) || 0; renderEntries(); });
    $("filterDate").addEventListener("change", function(){ filterDate = this.value; renderEntries(); });
    $("showHidden").addEventListener("change", function(){ showDotfiles = this.checked; renderEntries(); });
    $("bulkDownloadBtn").addEventListener("click", bulkDownload);
    $("logoutBtn").addEventListener("click", logout);

    /* Preview close */
    $("previewClose").addEventListener("click", closePreview);
    $("previewOverlay").addEventListener("click", function(ev){
      if (ev.target === this) closePreview();
    });

    /* Click outside ctx menu */
    document.addEventListener("click", function(ev){
      if (!ev.target.closest(".ctx-menu")) hideCtx();
    });

    /* Click outside modal */
    $("modalBackdrop").addEventListener("click", function(ev){
      if (ev.target === this) hideModal();
    });

    /* Drag and drop */
    document.addEventListener("dragenter", function(ev){
      ev.preventDefault();
      if (!IS_ADMIN) return;
      dragCount++;
      $("dropOverlay").classList.add("show");
    });
    document.addEventListener("dragleave", function(ev){
      ev.preventDefault();
      dragCount--;
      if (dragCount <= 0){
        dragCount = 0;
        $("dropOverlay").classList.remove("show");
      }
    });
    document.addEventListener("dragover", function(ev){
      ev.preventDefault();
      if (!IS_ADMIN) return;
    });
    document.addEventListener("drop", function(ev){
      ev.preventDefault();
      if (!IS_ADMIN) return;
      dragCount = 0;
      $("dropOverlay").classList.remove("show");
      var items = [];
      if (ev.dataTransfer && ev.dataTransfer.items) {
        var pending = 0;
        function traverseFileTree(item, path) {
          path = path || "";
          if (item.isFile) {
            pending++;
            item.file(function(file) {
              file.filepath = path + file.name;
              items.push(file);
              pending--;
              if (pending === 0 && items.length > 0) handleFiles(items);
            });
          } else if (item.isDirectory) {
            pending++;
            var dirReader = item.createReader();
            var readEntries = function() {
              dirReader.readEntries(function(entries) {
                if (entries.length === 0) {
                  pending--;
                  if (pending === 0 && items.length > 0) handleFiles(items);
                } else {
                  for (var i=0; i<entries.length; i++) {
                    traverseFileTree(entries[i], path + item.name + "/");
                  }
                  readEntries();
                }
              });
            };
            readEntries();
          }
        }
        for (var i = 0; i < ev.dataTransfer.items.length; i++) {
          var item = ev.dataTransfer.items[i].webkitGetAsEntry();
          if (item) traverseFileTree(item);
        }
        if (pending === 0 && items.length > 0) handleFiles(items);
      } else if (ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files.length > 0) {
        for (var i = 0; i < ev.dataTransfer.files.length; i++) items.push(ev.dataTransfer.files[i]);
        handleFiles(items);
      }
    });

    /* Paste */
    document.addEventListener("paste", function(ev){
      if (!IS_ADMIN) return;
      var items = ev.clipboardData && ev.clipboardData.items;
      if (!items) return;
      var files = [];
      for (var i = 0; i < items.length; i++){
        if (items[i].kind === "file"){
          var f = items[i].getAsFile();
          if (f){
            if (f.name === "image.png" || !f.name){
              var now = new Date();
              var ts = now.getFullYear() +
                String(now.getMonth()+1).padStart(2,"0") +
                String(now.getDate()).padStart(2,"0") + "_" +
                String(now.getHours()).padStart(2,"0") +
                String(now.getMinutes()).padStart(2,"0") +
                String(now.getSeconds()).padStart(2,"0");
              var ext = f.type ? "." + f.type.split("/")[1] : ".png";
              var newFile = new File([f], "paste_" + ts + ext, {type: f.type});
              files.push(newFile);
            } else {
              files.push(f);
            }
          }
        }
      }
      if (files.length > 0) handleFiles(files);
    });

    /* Keyboard */
    document.addEventListener("keydown", function(ev){
      /* Escape */
      if (ev.key === "Escape"){
        if ($("previewOverlay").classList.contains("show")){
          closePreview();
          return;
        }
        if ($("modalBackdrop").classList.contains("show")){
          hideModal();
          return;
        }
        var si = $("searchInput");
        if (document.activeElement === si){
          si.value = "";
          si.blur();
          isSearching = false;
          loadDirectory();
          return;
        }
      }
      /* Do not intercept when focused on inputs */
      if (document.activeElement && (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA")) return;
      /* / or Ctrl+F to focus search */
      if (ev.key === "/" || (ev.ctrlKey && ev.key === "f")){
        ev.preventDefault();
        $("searchInput").focus();
      }
      /* Delete key */
      if (ev.key === "Delete" && selected.size > 0){
        bulkDelete();
      }
    });

    /* Sort headers */
    $("sortHeader").addEventListener("click", function(ev){
      var col = ev.target.closest(".sort-col[data-sort]");
      if (col) setSort(col.getAttribute("data-sort"));
    });

    /* Breadcrumbs */
    $("breadcrumbs").addEventListener("click", function(ev){
      var crumb = ev.target.closest(".crumb");
      if (crumb){
        var p = crumb.getAttribute("data-path");
        if (p) navigate(p);
      }
    });

    /* File list delegation */
    var fl = $("fileList");
    fl.addEventListener("click", function(ev){
      /* Checkbox */
      if (ev.target.classList.contains("row-cb")){
        var row = ev.target.closest(".file-row");
        if (row) toggleSelect(row.getAttribute("data-name"), ev.target.checked);
        return;
      }
      /* Action buttons */
      var dlBtn = ev.target.closest(".action-download");
      if (dlBtn){
        /* let default link behavior handle download */
        return;
      }
      var renBtn = ev.target.closest(".action-rename");
      if (renBtn){
        ev.preventDefault();
        showRename(renBtn.getAttribute("data-name"));
        return;
      }
      var delBtn = ev.target.closest(".action-delete");
      if (delBtn){
        ev.preventDefault();
        confirmDelete([delBtn.getAttribute("data-name")]);
        return;
      }
      var copyBtn = ev.target.closest(".action-copy");
      if (copyBtn){
        ev.preventDefault();
        copyLink(copyBtn.getAttribute("data-name"));
        return;
      }
      var zipBtn = ev.target.closest(".action-zip");
      if (zipBtn){
        ev.preventDefault();
        downloadFolderZip(zipBtn.getAttribute("data-name"));
        return;
      }
      /* Name link */
      var link = ev.target.closest(".file-name-link");
      if (link){
        ev.preventDefault();
        var linkRow = link.closest(".file-row");
        var t = linkRow ? linkRow.getAttribute("data-type") : "file";
        var n = link.getAttribute("data-name");
        if (t === "dir"){
          navigate(currentPath + n + "/");
        } else {
          previewFile(n);
        }
        return;
      }
    });

    /* Context menu on file list */
    fl.addEventListener("contextmenu", function(ev){
      var row = ev.target.closest(".file-row");
      if (row){
        var n = row.getAttribute("data-name");
        showCtx(ev, n);
      }
    });

    /* Popstate */
    window.addEventListener("popstate", function(ev){
      if (ev.state && ev.state.path){
        currentPath = ev.state.path;
      } else {
        currentPath = decodeURIComponent(window.location.pathname);
        if (currentPath.charAt(currentPath.length - 1) !== "/") currentPath += "/";
      }
      isSearching = false;
      $("searchInput").value = "";
      selected.clear();
      loadDirectory();
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
</script>
</body>
</html>"""


#!/usr/bin/env python3
"""FileStation v2.0 - Enhanced file server backend with session auth, zip downloads, and modern web UI."""

import os, sys, ssl, json, time, base64, shutil, argparse
import mimetypes, threading, subprocess, urllib.parse
import secrets, zipfile, tempfile
from http.server import BaseHTTPRequestHandler

try:
    from http.server import ThreadingHTTPServer as HTTPServer
except ImportError:
    from http.server import HTTPServer



# ─── Constants ────────────────────────────────────────────────────────────────
VERSION = "2.0"
CHUNK = 256 * 1024
DEFAULT_MAX_UPLOAD = 2 * 1024 ** 3
SESSION_MAX_AGE = 86400  # 24 hours

# ANSI colors
RST = "\033[0m"
DIM = "\033[2m"
BLD = "\033[1m"
MC = {"GET": "\033[32m", "PUT": "\033[33m", "POST": "\033[34m", "DELETE": "\033[31m", "HEAD": "\033[2m"}

# ─── Global State ─────────────────────────────────────────────────────────────
_sessions = {}   # token -> {"user": str, "created": float}
_zip_keys = {}   # key -> {"paths": list, "created": float}

# ─── Helper Functions ─────────────────────────────────────────────────────────

def human_size(b):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {u}" if u != "B" else f"{int(b)} B"
        b /= 1024
    return f"{b:.1f} PB"


def safe_path(base, *parts):
    joined = os.path.join(base, *[p.lstrip("/") for p in parts])
    full = os.path.realpath(joined)
    base_real = os.path.realpath(base)
    if full != base_real and not full.startswith(base_real + os.sep):
        return None
    return full


def disk_info(path):
    u = shutil.disk_usage(path)
    return {"total": u.total, "used": u.used, "free": u.free}


def mime_type(path):
    t, _ = mimetypes.guess_type(path)
    return t or "application/octet-stream"


# ─── Session Functions ────────────────────────────────────────────────────────

def create_session(username):
    token = secrets.token_urlsafe(32)
    _sessions[token] = {"user": username, "created": time.time()}
    return token


def validate_session(token):
    session = _sessions.get(token)
    if session is None:
        return None
    if time.time() - session["created"] > SESSION_MAX_AGE:
        _sessions.pop(token, None)
        return None
    return session["user"]


def destroy_session(token):
    _sessions.pop(token, None)


def cleanup_old():
    now = time.time()
    expired_sessions = [t for t, s in _sessions.items() if now - s["created"] > SESSION_MAX_AGE]
    for t in expired_sessions:
        _sessions.pop(t, None)
    expired_zips = [k for k, v in _zip_keys.items() if now - v["created"] > 300]
    for k in expired_zips:
        _zip_keys.pop(k, None)


# ─── Login Page ───────────────────────────────────────────────────────────────

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FileStation - Sign In</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='10' y='25' width='80' height='60' rx='8' fill='%238b5cf6'/><rect x='10' y='20' width='35' height='15' rx='6' fill='%237c3aed'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{
  height:100%;
  font-family:'Inter',system-ui,-apple-system,sans-serif;
  background:#09090b;
  color:#fafafa;
  -webkit-font-smoothing:antialiased;
}
body{
  display:flex;
  align-items:center;
  justify-content:center;
  min-height:100vh;
  padding:20px;
}
@keyframes slideUp{
  from{opacity:0;transform:translateY(24px)}
  to{opacity:1;transform:translateY(0)}
}
.card{
  width:100%;
  max-width:400px;
  background:#18181b;
  border:1px solid #3f3f46;
  border-radius:16px;
  padding:40px 32px;
  box-shadow:0 16px 64px rgba(0,0,0,0.5),0 0 0 1px rgba(139,92,246,0.05);
  animation:slideUp 0.4s ease;
}
.logo{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  margin-bottom:8px;
}
.logo svg{width:32px;height:32px;color:#8b5cf6}
.logo-text{font-size:22px;font-weight:700;color:#8b5cf6}
.subtitle{
  text-align:center;
  color:#71717a;
  font-size:14px;
  margin-bottom:28px;
}
.error-msg{
  display:none;
  background:rgba(239,68,68,0.12);
  border:1px solid rgba(239,68,68,0.25);
  border-radius:8px;
  padding:10px 14px;
  font-size:13px;
  color:#fca5a5;
  margin-bottom:16px;
  text-align:center;
}
.error-msg.show{display:block}
.field{margin-bottom:16px}
.field label{
  display:block;
  font-size:13px;
  font-weight:500;
  color:#a1a1aa;
  margin-bottom:6px;
}
.field input{
  width:100%;
  padding:11px 14px;
  background:#27272a;
  border:1px solid #3f3f46;
  border-radius:8px;
  color:#fafafa;
  font-size:14px;
  font-family:inherit;
  outline:none;
  transition:border-color 0.2s,box-shadow 0.2s;
}
.field input:focus{
  border-color:#8b5cf6;
  box-shadow:0 0 0 3px rgba(139,92,246,0.15);
}
.field input::placeholder{color:#52525b}
.submit-btn{
  width:100%;
  padding:12px;
  background:#8b5cf6;
  color:#fff;
  border:none;
  border-radius:8px;
  font-size:15px;
  font-weight:600;
  font-family:inherit;
  cursor:pointer;
  transition:background 0.2s,transform 0.1s;
  margin-top:8px;
}
.submit-btn:hover{background:#7c3aed}
.submit-btn:active{transform:scale(0.98)}
.submit-btn:disabled{opacity:0.6;cursor:not-allowed}
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
    </svg>
    <span class="logo-text">FileStation</span>
  </div>
  <p class="subtitle">Sign in to continue</p>
  <div class="error-msg" id="errorMsg"></div>
  <form id="loginForm" autocomplete="on">
    <div class="field">
      <label for="username">Username</label>
      <input type="text" id="username" name="username" placeholder="Enter username" autocomplete="username" required>
    </div>
    <div class="field">
      <label for="password">Password</label>
      <input type="password" id="password" name="password" placeholder="Enter password" autocomplete="current-password" required>
    </div>
    <button type="submit" class="submit-btn" id="submitBtn">Sign In</button>
  </form>
</div>
<script>
(function(){
  var form = document.getElementById("loginForm");
  var btn = document.getElementById("submitBtn");
  var errDiv = document.getElementById("errorMsg");

  function getNextUrl(){
    var search = window.location.search || "";
    var params = search.replace("?", "").split("&");
    for (var i = 0; i < params.length; i++){
      var pair = params[i].split("=");
      if (pair[0] === "next" && pair[1]){
        return decodeURIComponent(pair[1]);
      }
    }
    return "/";
  }

  form.addEventListener("submit", function(ev){
    ev.preventDefault();
    var user = document.getElementById("username").value;
    var pass = document.getElementById("password").value;
    if (!user || !pass) return;

    btn.disabled = true;
    btn.textContent = "Signing in...";
    errDiv.classList.remove("show");

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/_api/login", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function(){
      var data;
      try { data = JSON.parse(xhr.responseText); } catch(e) { data = {}; }
      if (xhr.status >= 200 && xhr.status < 300 && data.ok){
        window.location.href = getNextUrl();
      } else {
        errDiv.textContent = data.error || "Invalid credentials";
        errDiv.classList.add("show");
        btn.disabled = false;
        btn.textContent = "Sign In";
      }
    };
    xhr.onerror = function(){
      errDiv.textContent = "Network error. Please try again.";
      errDiv.classList.add("show");
      btn.disabled = false;
      btn.textContent = "Sign In";
    };
    xhr.send(JSON.stringify({"username": user, "password": pass}));
  });
})();
</script>
</body>
</html>"""


# ─── Handler Class ────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    public_mode = False
    base_dir = "."
    auth_user = ""
    auth_pass = ""
    max_upload = DEFAULT_MAX_UPLOAD
    server_version = "FileStation/" + VERSION

    def log_request(self, code="-", size="-"):
        try:
            cmd = getattr(self, 'command', '-') or '-'
            raw_path = getattr(self, 'path', '/') or '/'
            c = MC.get(cmd, "")
            ts = time.strftime("%H:%M:%S")
            p = urllib.parse.unquote(urllib.parse.urlparse(raw_path).path)
            if len(p) > 60:
                p = p[:57] + "..."
            sc = "\033[32m" if str(code).startswith("2") else "\033[33m" if str(code).startswith("3") else "\033[31m"
            print(f"{DIM}{ts}{RST}  {c}{cmd:7s}{RST} {p:60s} {sc}{code}{RST}")
        except Exception:
            pass

    def log_message(self, fmt, *args):
        pass  # suppress default logs

    def finish(self):
        try:
            super().finish()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    # ── Auth Methods ──────────────────────────────────────────────────────

    def _get_session_token(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("session="):
                return part[8:]
        return None

    def _check_auth(self, require_admin=False):
        if not self.auth_user:
            return True
        if self.public_mode and not require_admin:
            return True
        
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            try:
                u, p = base64.b64decode(auth.split(None, 1)[1]).decode().split(":", 1)
                if u == self.auth_user and p == self.auth_pass:
                    return True
            except Exception:
                pass
                
        token = self._get_session_token()
        if token and validate_session(token):
            return True
            
        if not require_admin and "text/html" in self.headers.get("Accept", ""):
            self.send_response(302)
            self.send_header("Location", f"/_login?next={urllib.parse.quote(self.path)}")
            self.end_headers()
            return False
            
        self._send_401()
        return False

    def _send_401(self):
        body = b"Authentication required\n"
        self.send_response(401)
        if self.command in ("GET", "HEAD") and "text/html" in self.headers.get("Accept", ""):
            self.send_header("WWW-Authenticate", 'Basic realm="FileStation"')
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _enforce_https(self):
        if not getattr(self, "force_https", False):
            return False
        if isinstance(self.connection, ssl.SSLSocket):
            return False
        host = self.headers.get("Host", "")
        if not host:
            return False
        domain = host.split(":")[0]
        port_str = f":{self.https_port}" if self.https_port != 443 else ""
        target_url = f"https://{domain}{port_str}{self.path}"
        self.send_response(301)
        self.send_header("Location", target_url)
        self.end_headers()
        return True

    # ── Response Helpers ──────────────────────────────────────────────────

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_with_cookie(self, obj, cookie_str, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Set-Cookie", cookie_str)
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html, status=200):
        body = html.encode() if isinstance(html, str) else html
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text(self, text, status=200):
        body = text.encode() if isinstance(text, str) else text
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self, max_len=1048576):
        length = int(self.headers.get("Content-Length", 0))
        if length > max_len:
            return None
        try:
            return json.loads(self.rfile.read(length))
        except Exception:
            return None

    def _resolve(self, url_path):
        decoded = urllib.parse.unquote(url_path).lstrip("/")
        return safe_path(self.base_dir, decoded)

    # ── Auth API ──────────────────────────────────────────────────────────

    def _api_login(self):
        data = self._read_json()
        if not data:
            return self._json({"error": "Invalid request"}, 400)
        username = data.get("username", "")
        password = data.get("password", "")
        if username == self.auth_user and password == self.auth_pass:
            token = create_session(username)
            cookie = "session=" + token + "; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400"
            return self._json_with_cookie({"ok": True}, cookie)
        return self._json({"error": "Invalid credentials"}, 401)

    def _api_logout(self):
        token = self._get_session_token()
        if token:
            destroy_session(token)
        cookie = "session=; Path=/; HttpOnly; Max-Age=0"
        return self._json_with_cookie({"ok": True}, cookie)

    # ── File API ──────────────────────────────────────────────────────────

    def _api_list(self, dir_path):
        fs = self._resolve(dir_path)
        if not fs or not os.path.isdir(fs):
            return self._json({"error": "Not found"}, 404)
        entries = []
        try:
            for name in sorted(os.listdir(fs)):
                fp = os.path.join(fs, name)
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                e = {"name": name, "modified": st.st_mtime}
                if os.path.isdir(fp):
                    e["type"] = "dir"
                    try:
                        e["children"] = len(os.listdir(fp))
                    except (PermissionError, OSError):
                        e["children"] = 0
                else:
                    e["type"] = "file"
                    e["size"] = st.st_size
                    e["ext"] = os.path.splitext(name)[1].lower()
                entries.append(e)
        except PermissionError:
            return self._json({"error": "Permission denied"}, 403)
        self._json({"path": dir_path, "entries": entries, "disk": disk_info(fs)})

    def _api_search(self, query, base):
        fs = self._resolve(base)
        if not fs or not os.path.isdir(fs):
            return self._json({"error": "Not found"}, 404)
        results, ql = [], query.lower()
        for root, dirs, files in os.walk(fs):
            for name in dirs + files:
                if ql in name.lower():
                    fp = os.path.join(root, name)
                    try:
                        st = os.stat(fp)
                    except OSError:
                        continue
                    r = {"name": name, "path": "/" + os.path.relpath(fp, self.base_dir), "modified": st.st_mtime}
                    r["type"] = "dir" if os.path.isdir(fp) else "file"
                    if r["type"] == "file":
                        r["size"] = st.st_size
                        r["ext"] = os.path.splitext(name)[1].lower()
                    results.append(r)
                    if len(results) >= 200:
                        break
            if len(results) >= 200:
                break
        self._json({"query": query, "results": results})

    def _api_delete(self):
        data = self._read_json()
        if not data:
            return self._json({"error": "Invalid request"}, 400)
        paths = data.get("paths", [])
        deleted, errors = [], []
        base_real = os.path.realpath(self.base_dir)
        for p in paths:
            fs = self._resolve(p)
            if not fs or fs == base_real:
                errors.append({"path": p, "error": "Invalid path"})
                continue
            try:
                if os.path.isdir(fs):
                    shutil.rmtree(fs)
                elif os.path.isfile(fs) or os.path.islink(fs):
                    os.remove(fs)
                else:
                    errors.append({"path": p, "error": "Not found"})
                    continue
                deleted.append(p)
            except OSError as e:
                errors.append({"path": p, "error": str(e)})
        self._json({"deleted": deleted, "errors": errors})

    def _api_rename(self):
        data = self._read_json()
        if not data:
            return self._json({"error": "Invalid request"}, 400)
        src, dst = data.get("from", ""), data.get("to", "")
        if not src or not dst:
            return self._json({"error": "Missing from/to"}, 400)
        src_fs, dst_fs = self._resolve(src), self._resolve(dst)
        if not src_fs or not dst_fs:
            return self._json({"error": "Invalid path"}, 400)
        if not os.path.exists(src_fs):
            return self._json({"error": "Source not found"}, 404)
        if os.path.exists(dst_fs):
            return self._json({"error": "Destination exists"}, 409)
        try:
            os.makedirs(os.path.dirname(dst_fs), exist_ok=True)
            shutil.move(src_fs, dst_fs)
            self._json({"ok": True})
        except OSError as e:
            self._json({"error": str(e)}, 500)

    def _api_mkdir(self):
        data = self._read_json()
        if not data:
            return self._json({"error": "Invalid request"}, 400)
        path = data.get("path", "")
        if not path:
            return self._json({"error": "Missing path"}, 400)
        fs = self._resolve(path)
        if not fs:
            return self._json({"error": "Invalid path"}, 400)
        if os.path.exists(fs):
            return self._json({"error": "Already exists"}, 409)
        try:
            os.makedirs(fs)
            self._json({"ok": True})
        except OSError as e:
            self._json({"error": str(e)}, 500)

    def _api_zip_prepare(self):
        data = self._read_json()
        if not data:
            return self._json({"error": "Invalid request"}, 400)
        paths = data.get("paths", [])
        if not paths:
            return self._json({"error": "No paths specified"}, 400)
        # Validate each path exists
        resolved = []
        for p in paths:
            fs = self._resolve(p)
            if not fs or not os.path.exists(fs):
                return self._json({"error": "Path not found: " + p}, 404)
            resolved.append(fs)
        # Generate key and store
        key = secrets.token_urlsafe(16)
        _zip_keys[key] = {"paths": resolved, "created": time.time()}
        # Determine filename
        if len(resolved) == 1:
            filename = os.path.basename(resolved[0]) + ".zip"
        else:
            filename = "download.zip"
        cleanup_old()
        return self._json({"key": key, "filename": filename})

    def _serve_zip(self, key):
        entry = _zip_keys.pop(key, None)
        if not entry:
            return self._json({"error": "Invalid or expired download key"}, 404)
        if time.time() - entry["created"] > 300:
            return self._json({"error": "Download key expired"}, 410)
        paths = entry["paths"]
        tmp = tempfile.SpooledTemporaryFile(max_size=64 * 1024 * 1024)
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                for fspath in paths:
                    if os.path.isfile(fspath):
                        zf.write(fspath, os.path.basename(fspath))
                    elif os.path.isdir(fspath):
                        dirname = os.path.basename(fspath)
                        for root, dirs, files in os.walk(fspath):
                            for fname in files:
                                full = os.path.join(root, fname)
                                arcname = os.path.join(dirname, os.path.relpath(full, fspath))
                                zf.write(full, arcname)
            # Get size
            tmp.seek(0, 2)
            size = tmp.tell()
            tmp.seek(0)
            # Determine filename for Content-Disposition
            if len(paths) == 1:
                dl_name = os.path.basename(paths[0]) + ".zip"
            else:
                dl_name = "download.zip"
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", "attachment; filename=\"" + dl_name + "\"")
            self.send_header("Content-Length", str(size))
            self.end_headers()
            while True:
                chunk = tmp.read(CHUNK)
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break
        finally:
            tmp.close()

    # ── File Serving ──────────────────────────────────────────────────────

    def _serve_file(self, fs_path, head_only=False):
        try:
            st = os.stat(fs_path)
        except OSError:
            return self.send_error(404)
        fsize = st.st_size
        ctype = mime_type(fs_path)

        # Range support
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            try:
                spec = rng[6:]
                if spec.startswith("-"):
                    start, end = max(0, fsize - int(spec[1:])), fsize - 1
                elif spec.endswith("-"):
                    start, end = int(spec[:-1]), fsize - 1
                else:
                    parts = spec.split("-", 1)
                    start, end = int(parts[0]), int(parts[1])
                if start > end or start >= fsize:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{fsize}")
                    self.end_headers()
                    return
                end = min(end, fsize - 1)
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(length))
                self.send_header("Content-Range", f"bytes {start}-{end}/{fsize}")
                self.send_header("Accept-Ranges", "bytes")
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                if not qs.get("preview"):
                    self.send_header("Content-Disposition", f"attachment; filename=\"{urllib.parse.quote(os.path.basename(fs_path))}\"")
                self.end_headers()
                if head_only:
                    return
                with open(fs_path, "rb") as f:
                    f.seek(start)
                    rem = length
                    while rem > 0:
                        chunk = f.read(min(CHUNK, rem))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        rem -= len(chunk)
                return
            except (ValueError, IndexError):
                pass

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(fsize))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", self.date_time_string(st.st_mtime))
        self.send_header("X-Content-Type-Options", "nosniff")
        
        # Force download unless ?preview=1 is present
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if not qs.get("preview"):
            self.send_header("Content-Disposition", f"attachment; filename=\"{urllib.parse.quote(os.path.basename(fs_path))}\"")
            
        self.end_headers()
        if head_only:
            return
        with open(fs_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break

    # ── HTTP Methods ──────────────────────────────────────────────────────

    def do_GET(self):
        if self._enforce_https():
            return
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # Login page — NO auth required
        if path == "/_login":
            return self._html(LOGIN_HTML)

        # Zip download — requires auth
        if path == "/_api/zip-dl":
            if not self._check_auth():
                return
            key = qs.get("key", [""])[0]
            if not key:
                return self._json({"error": "Missing key"}, 400)
            return self._serve_zip(key)

        # Everything below requires auth
        if not self._check_auth():
            return

        if path == "/_api/list":
            return self._api_list(qs.get("path", ["/"])[0])
        if path == "/_api/search":
            return self._api_search(qs.get("q", [""])[0], qs.get("path", ["/"])[0])
        if path == "/_api/disk":
            return self._json(disk_info(self.base_dir))

        fs = self._resolve(path)
        if not fs:
            return self.send_error(403)
        if os.path.isdir(fs):
            if not path.endswith("/"):
                self.send_response(301)
                loc = path + "/"
                if parsed.query:
                    loc += "?" + parsed.query
                self.send_header("Location", loc)
                self.end_headers()
                return
            html = UI_HTML.replace("__MAX_UPLOAD__", str(self.max_upload))
            is_admin = "true"
            if self.public_mode:
                token = self._get_session_token()
                if not (token and validate_session(token)):
                    auth = self.headers.get("Authorization", "")
                    if not auth.startswith("Basic "):
                        is_admin = "false"
                    else:
                        try:
                            u, p = base64.b64decode(auth.split(None, 1)[1]).decode().split(":", 1)
                            if u != self.auth_user or p != self.auth_pass:
                                is_admin = "false"
                        except Exception:
                            is_admin = "false"
            html = html.replace("__IS_ADMIN__", is_admin)
            return self._html(html)
        if os.path.isfile(fs):
            return self._serve_file(fs)
        self.send_error(404)

    def do_HEAD(self):
        if self._enforce_https():
            return
        if not self._check_auth():
            return
        fs = self._resolve(urllib.parse.unquote(urllib.parse.urlparse(self.path).path))
        if not fs:
            return self.send_error(403)
        if os.path.isfile(fs):
            return self._serve_file(fs, head_only=True)
        self.send_error(404)

    def do_PUT(self):
        if not self._check_auth(require_admin=True):
            return
        length = int(self.headers.get("Content-Length", 0))
        crange = self.headers.get("Content-Range")
        start_byte = 0
        total_size = length
        if crange and crange.startswith("bytes "):
            try:
                rng, tot = crange[6:].split("/")
                start_byte = int(rng.split("-")[0])
                total_size = int(tot)
            except Exception:
                pass

        if total_size > self.max_upload:
            self.send_error(413, f"Max upload: {human_size(self.max_upload)}")
            rem = length
            while rem > 0:
                chunk = self.rfile.read(min(CHUNK, rem))
                if not chunk: break
                rem -= len(chunk)
            return

        di = disk_info(self.base_dir)
        if length > di["free"] - 100 * 1024 * 1024:
            return self.send_error(507, "Not enough disk space")
            
        fs = self._resolve(urllib.parse.unquote(urllib.parse.urlparse(self.path).path))
        if not fs or fs == os.path.realpath(self.base_dir):
            return self.send_error(403)
            
        os.makedirs(os.path.dirname(fs), exist_ok=True)
        mode = "r+b" if start_byte > 0 and os.path.exists(fs) else "wb"
        try:
            with open(fs, mode) as f:
                if start_byte > 0:
                    f.seek(start_byte)
                rem = length
                while rem > 0:
                    chunk = self.rfile.read(min(CHUNK, rem))
                    if not chunk:
                        break
                    f.write(chunk)
                    rem -= len(chunk)
            self._text("Uploaded\n", 201)
        except OSError as e:
            self.send_error(500, str(e))

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        # Login — NO auth required
        if path == "/_api/login":
            return self._api_login()

        # Everything below requires at least read auth
        if not self._check_auth():
            return

        if path == "/_api/logout":
            return self._api_logout()
        if path == "/_api/zip":
            return self._api_zip_prepare()

        # Write operations require admin
        if not self._check_auth(require_admin=True):
            return

        if path == "/_api/delete":
            return self._api_delete()
        if path == "/_api/rename":
            return self._api_rename()
        if path == "/_api/mkdir":
            return self._api_mkdir()
        self.send_error(404, "Unknown endpoint")

    def do_DELETE(self):
        if not self._check_auth(require_admin=True):
            return
        fs = self._resolve(self.path)
        if not fs or fs == os.path.realpath(self.base_dir):
            return self.send_error(403)
        if not os.path.exists(fs):
            return self.send_error(404)
        try:
            if os.path.isdir(fs):
                shutil.rmtree(fs)
            else:
                os.remove(fs)
            self._text("Deleted\n")
        except OSError as e:
            self.send_error(500, str(e))


# ─── CLI Functions ────────────────────────────────────────────────────────────

def parse_size(s):
    s = s.strip().upper()
    for suffix, mult in [("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024), ("T", 1024**4), ("G", 1024**3), ("M", 1024**2), ("K", 1024), ("B", 1)]:
        if s.endswith(suffix):
            return int(float(s[: -len(suffix)]) * mult)
    return int(s)


def ensure_cert():
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        return
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", "key.pem", "-out", "cert.pem", "-days", "365", "-nodes", "-subj", "/CN=localhost"],
        check=True, capture_output=True,
    )


class SecureHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, ssl_context):
        super().__init__(server_address, RequestHandlerClass)
        self.ssl_context = ssl_context

    def process_request_thread(self, request, client_address):
        try:
            request.settimeout(10.0)  # 10s timeout for TLS handshake
            request = self.ssl_context.wrap_socket(request, server_side=True)
            request.settimeout(None)
            super().process_request_thread(request, client_address)
        except Exception:
            try:
                request.close()
            except Exception:
                pass


def main():
    p = argparse.ArgumentParser(description="FileStation v2.0 - Enhanced file server with web UI")
    p.add_argument("-p", "--port", type=int, default=80, help="HTTP port (default: 80)")
    p.add_argument("--https-port", type=int, default=443, help="HTTPS port (default: 443)")
    p.add_argument("-d", "--directory", default=os.getcwd(), help="Directory to serve")
    p.add_argument("-u", "--user", default=os.environ.get("FS_USER", "admin"), help="Username")
    p.add_argument("--password", default=os.environ.get("FS_PASS", "secret"), help="Password")
    p.add_argument("--public", action="store_true", help="Enable public mode (downloads without auth)")
    p.add_argument("--no-https", action="store_true", help="Disable HTTPS")
    p.add_argument("--no-http", action="store_true", help="Disable HTTP")
    p.add_argument("--force-https", action="store_true", help="Redirect all HTTP traffic to HTTPS")
    p.add_argument("--cert", help="Path to SSL certificate (default: auto-generated cert.pem)")
    p.add_argument("--key", help="Path to SSL private key (default: auto-generated key.pem)")
    p.add_argument("--max-upload", default="2G", help="Max upload size (default: 2G)")
    args = p.parse_args()

    Handler.base_dir = os.path.realpath(args.directory)
    Handler.auth_user = args.user
    Handler.auth_pass = args.password
    Handler.max_upload = parse_size(args.max_upload)
    Handler.public_mode = args.public
    Handler.force_https = args.force_https
    Handler.https_port = args.https_port

    print(f"\n  {BLD}FileStation v{VERSION}{RST}")
    print(f"  {'---' * 14}")
    print(f"  Directory:  {Handler.base_dir}")
    print(f"  Auth:       {args.user}:{'*' * len(args.password)}")
    print(f"  Max upload: {human_size(Handler.max_upload)}")
    print()

    servers = []
    if not args.no_http:
        srv = HTTPServer(("0.0.0.0", args.port), Handler)
        print(f"  HTTP  -> http://0.0.0.0:{args.port}/")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)

    if not args.no_https:
        cert_file = args.cert or "cert.pem"
        key_file = args.key or "key.pem"
        if not args.cert or not args.key:
            ensure_cert()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert_file, key_file)
        srv = SecureHTTPServer(("0.0.0.0", args.https_port), Handler, ctx)
        print(f"  HTTPS -> https://0.0.0.0:{args.https_port}/")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)

    print(f"\n  Press Ctrl+C to stop\n")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print(f"\n  Shutting down...")
        for s in servers:
            s.shutdown()
        print(f"  Stopped.\n")


if __name__ == "__main__":
    main()
