<p align="center">
  <img src="https://img.icons8.com/color/144/000000/folder-invoices--v1.png" alt="FileStation Logo"/>
  <br/>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=200&section=header&text=FileStation&fontSize=60&fontColor=ffffff&animation=twinkling&fontAlignY=35&desc=Lightning-fast%20Python%20web%20file%20manager&descAlignY=55&descSize=18"/>
</p>
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:6C63FF,100:00D4FF&height=3"/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/>
  <img src="https://img.shields.io/badge/Dependencies-Zero-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Version-3.1-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/HTTPS-Let's%20Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white"/>
</p>

FileStation is a production-ready, ultra-lightweight web server that turns any Linux directory into a beautiful, secure, and modern file management interface. The entire backend, frontend HTML, CSS, and vanilla JS are packed into a single `server.py` file with **zero Python dependencies** (just standard Python 3.7+).

<p align="center">
  <img src="https://github.com/user-attachments/assets/9eca2dc6-0f52-4711-939e-04c1c85be41c" alt="FileStation UI Preview" width="600"/>
</p>

## ✨ Key Features

- **Single-File Architecture:** The entire backend, frontend HTML, CSS, and vanilla JS are packed into a single `server.py` file. Just drop it and run.
- **Multithreaded & Concurrency-Capped:** Requests are handled in parallel threads (bounded to 48) so a large upload, video stream, or zip download never blocks browsing, listing, or other uploads. No more lag or frozen UI.
- **Resumable Chunked Uploads:** Upload massive files (5GB+ ISOs/videos). Files are pushed in 2MB chunks using `Content-Range` and can resume from a previous offset. Uploads are size-verified on completion so nothing is silently truncated.
- **Real Video Thumbnails:** `GET <video>?thumb=1` generates a cached preview frame (via `ffmpeg`, optional) shown in the grid view. Falls back to a badge gracefully when ffmpeg is not installed.
- **Read-Only Previews for Guests:** Clicking a file previews it inline — Markdown (`.md`) renders formatted, code/text files show as readable content, PDFs open in an embedded viewer — without requiring login. Download is always one click away.
- **Clipboard Paste-to-Upload:** Copy an image (or any file) anywhere and press `Ctrl+V` in the page to upload it instantly to the current folder.
- **Grid Multi-Select & Bulk Actions:** Select multiple files in list or grid view, then Download (as zip), Move, or Delete in one action.
- **Folder Drag-and-Drop:** Drag entire nested folder trees directly from your desktop into the browser. FileStation recursively reads them and recreates the exact structure on your server.
- **Rich Media Streaming:** Natively streams videos and audio with HTTP `Range` seeking, ETag caching, and `Accept-Ranges`. Upload `.mp4`/`.webm` and play straight from the browser.
- **Built-in HTTPS & Let's Encrypt:** Native integration for SSL. It automatically handles HTTPS redirects and serves your Let's Encrypt certificates directly. The server never auto-generates certs — pass `--cert` and `--key` (or let the installer generate a self-signed one) to enable the HTTPS listener.
- **Public vs. Admin Modes:** Securely lock down your server with Basic Auth, or enable `--public` mode to let guests view, preview, and download files while blocking all uploads, moves, and deletions. No annoying browser password prompts for guests!
- **Security Hardened:** Strict path-traversal protection, TLS handshake timeouts, `X-Content-Type-Options`, `X-Frame-Options`, a Content-Security-Policy, and XSS-safe rendering of filenames and file contents.
- **CLI & AI-Agent Friendly:** Everything is a plain HTTP endpoint — upload with `curl -T`, download with `curl -O`, list/search folders as JSON. Works great from terminals and LLM harnesses.
- **Premium Glassmorphic UI:** A meticulously designed dark-mode interface with smooth animations, grid/list views, mobile responsiveness, and bulk-action toolbars.

## 🚀 One-Click Installation (Debian/Ubuntu)

The fastest way to deploy FileStation with systemd management and automatic Let's Encrypt SSL certificates is using the included installer script.

## Download the files to your server and run

```bash
wget https://raw.githubusercontent.com/DDreamer01/FileStation/main/server.py https://raw.githubusercontent.com/DDreamer01/FileStation/main/install.sh && chmod +x install.sh && sudo ./install.sh
```

The interactive installer will ask you:

1. **Service Name:** Create multiple isolated spaces by running the script multiple times!
2. **Username & Password:** Set your admin credentials.
3. **Directory:** The path to serve (e.g., `/home/username/files`).
4. **Ports:** Defaults to `80` and `443`.
5. **Domain:** Enter your domain name to automatically fetch and configure HTTPS via Let's Encrypt.
6. **Self-signed HTTPS:** If you leave the domain blank, the installer can generate a self-signed certificate so HTTPS still works (default `y`).

The installer also installs `ffmpeg` (best-effort) so video thumbnails work out of the box.

## 🛠️ Manual Usage & CLI Options

If you don't want to run it as a system service, you can run `server.py` directly. **Python 3.7+ is required.**

```bash
wget https://raw.githubusercontent.com/DDreamer01/FileStation/main/server.py
```

```bash
python3 server.py -d /home/user/files -u admin --password secret
```

### Available Arguments:

| Flag | Description |
| :--- | :--- |
| `-d`, `--directory` | The root directory to serve (default: current directory). |
| `-u`, `--user` | Admin username (env: `FS_USER`, default `xoxo`). |
| `--password` | Admin password (env: `FS_PASS`, default `xoxo`). |
| `-p`, `--port` | HTTP port to listen on (default: `80`). |
| `--https-port` | HTTPS port to listen on (default: `443`). |
| `--cert` | Path to SSL certificate chain (`fullchain.pem`). Required (with `--key`) to enable the HTTPS listener. |
| `--key` | Path to SSL private key (`privkey.pem`). Required (with `--cert`) to enable the HTTPS listener. |
| `--force-https` | Redirects all HTTP traffic to HTTPS automatically. |
| `--public` | Allows unauthenticated users to view, preview, and download files (read-only). |
| `--max-upload` | Max upload size (e.g. `2G`, `500M`; default: `10G`). |
| `--thumb-dir` | Directory to cache video thumbnails (default: `~/.filestation_thumbs`). |
| `--no-http` | Disable the plain-HTTP listener. |
| `--no-https` | Disable the HTTPS listener. |
| `--nginx-prefix` | Nginx `X-Accel-Redirect` prefix for offloading file delivery (env: `FS_NGINX_PREFIX`). |

When in public mode, you can append `_login` to your domain/ip for logging in.

## 💻 CLI / API Usage for Scripts & AI Agents

FileStation speaks plain HTTP, so it integrates cleanly with `curl`, `wget`, and LLM agent harnesses.

```bash
HOST="http://your-server:9000"      # replace with your host:port
AUTH="user:password"                # admin credentials for write operations

# Upload a file (PUT)
curl -u "$AUTH" -T video.mp4 "$HOST/videos/video.mp4"

# Upload to a new subfolder (created automatically)
curl -u "$AUTH" -T report.pdf "$HOST/reports/q3/report.pdf"

# Download a file (attachment)
curl -u "$AUTH" -o video.mp4 "$HOST/videos/video.mp4"

# Download with resume (Range support)
curl -u "$AUTH" -C - -o video.mp4 "$HOST/videos/video.mp4"

# Inline preview (no Content-Disposition: attachment)
curl -u "$AUTH" "$HOST/README.md?preview=1"

# Video thumbnail frame (JPEG, cached server-side)
curl -u "$AUTH" "$HOST/videos/video.mp4?thumb=1" -o thumb.jpg

# Stream just a byte range (video seeking)
curl -u "$AUTH" -H "Range: bytes=1000000-2000000" "$HOST/videos/video.mp4?preview=1" -o chunk.mp4

# List a folder as JSON
curl "$HOST/_api/list?path=/videos"

# Search the tree as JSON (returns full paths)
curl "$HOST/_api/search?q=report&path=/"

# Create a folder / move / rename / delete (admin)
curl -u "$AUTH" -X POST -H "Content-Type: application/json" -d '{"path":"/newfolder"}' "$HOST/_api/mkdir"
curl -u "$AUTH" -X POST -H "Content-Type: application/json" -d '{"from":"/a.txt","to":"/b.txt"}' "$HOST/_api/rename"
curl -u "$AUTH" -X DELETE "$HOST/b.txt"

# Bulk download multiple files as one zip
curl -u "$AUTH" -X POST -H "Content-Type: application/json" -d '{"paths":["/a.mp4","/b.mp4"]}' "$HOST/_api/zip"
```

> **Tip:** In `--public` mode, GET/list/search/zip downloads work without auth; uploads, moves, renames, and deletes require admin login (Basic auth or session cookie).

## 📦 Requirements

- **Python 3.7+** (stdlib only — no `pip install` needed)
- **ffmpeg** *(optional)* — only required for video thumbnail generation; the UI degrades gracefully without it.
- **Linux** recommended.

## 🔒 Security Notes

- **Serving Directories:** It is highly recommended to serve a dedicated folder (e.g., `/home/username/public_files`) rather than the root `/home` or `/` directory to prevent exposing sensitive system dotfiles.
- **Path Traversal:** FileStation includes strict path resolution to prevent directory traversal attacks. Users cannot access files outside the specified root directory, and symlinks pointing outside the root are rejected.
- **Content Hardening:** Responses include `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive Content-Security-Policy, and referrer policy; filenames and rendered file contents are escaped to prevent stored XSS.
- **TLS Handshake Timeouts:** The server includes a custom secure socket wrapper to prevent malicious port scanners from hanging the server threads indefinitely.
- **Auth:** Admin access uses Basic auth or an HttpOnly session cookie (24h expiry). In `--public` mode guests are read-only.

**Developed by:** [†hε drεαmεr](https://t.me/DR34_M3R)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/DDreamer01/FileStation/issues).

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
