# StreamNest — Original DiskWala-style Web Viewer

An original FastAPI/Jinja/JavaScript project with a paste-link → server-side resolver → browser-player flow. It does not copy DiskWala.Net branding, source code, or UI.

## Structure

```text
StreamNest/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Set your authorized resolver configuration in `.env`:

```env
DISKWALA_PROXY_URL=your_proxy_endpoint
DISKWALA_API_KEY=your_secret_key
PORT=3000
```

Never commit `.env` or expose the API key in HTML/JavaScript.

Run:

```bash
python app.py
```

Open the forwarded port in Codespaces.

## Flow

```text
DiskWala URL
   ↓
POST /api/resolve
   ↓
Configured server-side resolver
   ↓
fileInfo.url
   ↓
Browser video player
```

The returned media must itself be playable by the browser. If the upstream server requires special headers, blocks browser playback, uses an unsupported codec, or returns a download-only response, the player may not work; this project does not bypass DRM or access controls.

Use only content and links you are authorized to access.

FastAPI's documented Jinja2 template and StaticFiles patterns are used for serving the original frontend.
