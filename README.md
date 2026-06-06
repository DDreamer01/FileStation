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
  <img src="https://img.shields.io/badge/HTTPS-Let's%20Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white"/>
</p>

FileStation is a production-ready, ultra-lightweight web server that turns any Linux directory into a beautiful, secure, and modern file management interface. With zero external dependencies (just standard Python 3), you can instantly deploy a premium file server anywhere.

<p align="center">
  <img src="https://sa.imagitech.online/Pictures/tennessee-daisy-flower-field-co86cuxoqq2t420l.jpg" alt="FileStation UI Preview" width="600"/>
</p>

## ✨ Key Features

- **Single-File Architecture:** The entire backend, frontend HTML, CSS, and vanilla JS are packed into a single `server.py` file. Just drop it and run.
- **Resumable Chunked Uploads:** Upload massive files (5GB+ ISOs/videos). Internet blipped? Just drag the file back in and it resumes instantly from where it left off.
- **Folder Drag-and-Drop:** Drag entire nested folder trees directly from your desktop into the browser. FileStation recursively reads them and recreates the exact structure on your server.
- **Rich Media Previews:** Natively streams videos and audio. Renders Markdown (`.md`) files beautifully, and provides syntax highlighting for code files (`.py`, `.js`, `.sh`, etc.) directly in the browser.
- **Built-in HTTPS & Let's Encrypt:** Native integration for SSL. It automatically handles HTTPS redirects and serves your Let's Encrypt certificates directly.
- **Public vs. Admin Modes:** Securely lock down your server with Basic Auth, or enable `--public` mode to let guests download and preview files while blocking all uploads and deletions. No annoying browser password prompts for guests!
- **Premium Glassmorphic UI:** A meticulously designed dark-mode interface with smooth animations, mobile responsiveness, and bulk-action toolbars.

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

## 🛠️ Manual Usage & CLI Options

If you don't want to run it as a system service, you can run `server.py` directly. **Python 3.7+ is required.**

```bash
python3 server.py -d /home/user/files -u admin --password secret
```

### Available Arguments:

| Flag | Description |
| :--- | :--- |
| `-d`, `--directory` | The root directory to serve (default: current directory). |
| `-u`, `--user` | Admin username. |
| `--password` | Admin password. |
| `-p`, `--port` | HTTP port to listen on (default: `80`). |
| `--https-port` | HTTPS port to listen on (default: `443`). |
| `--cert` | Path to SSL certificate chain (`fullchain.pem`). |
| `--key` | Path to SSL private key (`privkey.pem`). |
| `--force-https` | Redirects all HTTP traffic to HTTPS automatically. |
| `--public` | Allows unauthenticated users to view and download files (read-only). |
| `--max-upload` | Max upload size in GB (default: `2.0`). |

## 🔒 Security Notes

- **Serving Directories:** It is highly recommended to serve a dedicated folder (e.g., `/home/username/public_files`) rather than the root `/home` or `/` directory to prevent exposing sensitive system dotfiles.
- **Path Traversal:** FileStation includes strict path resolution to prevent directory traversal attacks. Users cannot access files outside the specified root directory.
- **TLS Handshake Timeouts:** The server includes a custom secure socket wrapper to prevent malicious port scanners from hanging the server threads indefinitely.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/YOUR_USERNAME/FileStation/issues).

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
