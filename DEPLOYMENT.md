# 🚀 Production Deployment Guide: AI Warehouse Intelligence

This platform is architected as a **unified high-performance web service**. The FastAPI backend can directly serve both the compiled React single-page frontend application, the computer vision APIs, and the CCTV video streaming on a single port (8000).

---

## ⚡ Quick Deployment Options

| Option | Best For | Time to Deploy | Cost |
| :--- | :--- | :--- | :--- |
| **Option 1: Render / Railway** | Live public web URL with free HTTPS for judges/clients | ~3 minutes | Free |
| **Option 2: Standalone On-Premises** | Warehouse local network / desktop server | 10 seconds | Free |
| **Option 3: Cloud VM (AWS / DigitalOcean / Linode)** | Dedicated production infrastructure | ~5 minutes | \–15/mo |
| **Option 4: Docker & Docker Compose** | Isolated containerized deployment | 2 minutes | Any host |
| **Option 5: Instant Live Tunnel (Cloudflare)** | Immediate public HTTPS link from your PC right now | 30 seconds | Free |

---

## 1️⃣ Option 1: Deploy to Render (1-Click / Git Push)

The repository includes pre-configured **
ender.yaml** and **Procfile**.

1. Push your repository to **GitHub** or **GitLab**.
2. Go to [https://render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render automatically detects the configuration:
   - **Environment**: \Python   - **Build Command**: \pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..   - **Start Command**: \python -m uvicorn backend.main:app --host 0.0.0.0 --port \
5. Click **Create Web Service**. Within ~3 minutes, your live URL (e.g. \https://ai-warehouse-intelligence.onrender.com\) is active with free automated SSL.

---

## 2️⃣ Option 2: Standalone Production Server (Local / Office / LAN)

Because the compiled production frontend is bundled with the backend, you only need **one single command** to run the complete app for your entire warehouse network:

### On Windows:
Double-click **\start_production.bat\** or run:
\\powershell
cd frontend && npm run build && cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
\
### On Linux / macOS:
\\ash
chmod +x start_production.sh
./start_production.sh
\
- **Access locally**: \http://localhost:8000- **Access across your local WiFi / LAN**: \http://<your-machine-ip>:8000\ (e.g. \http://192.168.1.50:8000\)

---

## 3️⃣ Option 3: Deploy to Ubuntu Cloud VM (AWS EC2 / DigitalOcean / Linode)

### Step 1: Clone and install dependencies
\\ash
git clone <your-repo-url> /opt/ai-warehouse-intelligence
cd /opt/ai-warehouse-intelligence

sudo apt update && sudo apt install -y python3-pip python3-venv nodejs npm ffmpeg libgl1-mesa-glx
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend && npm install && npm run build && cd ..
\
### Step 2: Create Systemd Background Service
Create \/etc/systemd/system/dockguard.service\:
\\ini
[Unit]
Description=AI Warehouse Intelligence Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/ai-warehouse-intelligence
ExecStart=/opt/ai-warehouse-intelligence/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
\Enable and start the service:
\\ash
sudo systemctl daemon-reload
sudo systemctl enable --now dockguard
\
### Step 3: Nginx Reverse Proxy with SSL
\ginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP \;
        proxy_set_header X-Forwarded-For \;
        proxy_read_timeout 300s;
        client_max_body_size 500M;
    }
}
\Issue free SSL:
\\ash
sudo certbot --nginx -d your-domain.com
\
---

## 4️⃣ Option 4: Docker & Docker Compose

For containerized deployment on any Docker host:

\\ash
docker-compose up -d --build
\
- Frontend runs on: \http://localhost:3000- Backend API runs on: \http://localhost:8000- CCTV Video storage volume persists in: \./uploads
---

## 5️⃣ Option 5: Instant Public Live HTTPS Demo (30 Seconds)

If you want an immediate public HTTPS link to share right now without registering for cloud services:

### Using Cloudflare Tunnel (Recommended, No signup needed):
\\powershell
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8000
\Cloudflare will instantly output a public URL like:
\https://random-words.trycloudflare.com\ -> anyone in the world can open and test your app!

### Using LocalTunnel (Node.js):
\\powershell
npx localtunnel --port 8000
\