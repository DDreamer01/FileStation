<div align="center">
  <img src="https://img.icons8.com/color/144/000000/folder-invoices--v1.png" alt="FileStation Logo">
  <h1>FileStation</h1>
  <p><b>A modern, lightning-fast, single-file Python web file manager.</b></p>
</div>

FileStation is a production-ready, ultra-lightweight web server that turns any Linux directory into a beautiful, secure, and modern file management interface. With zero external dependencies (just standard Python 3), you can instantly deploy a premium file server anywhere.

![FileStation UI Preview](https://i.imgur.com/PLACEHOLDER_UI.png) <!-- Feel free to add a screenshot here! -->

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

```bash
# Download the files to your server
wget https://raw.githubusercontent.com/YOUR_USERNAME/FileStation/main/server.py
wget https://raw.githubusercontent.com/YOUR_USERNAME/FileStation/main/install.sh

# Make the installer executable and run it
chmod +x install.sh
sudo ./install.sh
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
