# 📝 YT-AI-Notes

> **YouTube → Transcript → AI-Powered Notes, in seconds.**

YT-AI-Notes is a Fastapi web application that takes any YouTube video URL, extracts and transcribes its audio, and uses Google's Gemini AI to produce professional, well-structured study notes or articles.

---

## 🎯 How It Works

```
YouTube URL  ──►  yt-dlp (audio)  ──►  Faster-Whisper (transcript)  ──►  Gemini AI (notes)
```

| Step | Tool | What happens |
|------|------|--------------|
| **Extract** | `yt-dlp` + `ffmpeg` | Downloads high-quality audio from YouTube |
| **Transcribe** | `Faster-Whisper` | Converts speech to accurate text |
| **Generate** | `Gemini 2.5 Flash` | Transforms raw transcript into clean, structured notes |

---

## 🚀 Features

- 🔗 **Seamless URL Processing** — Paste any YouTube link and go
- 🎙️ **Automated Audio Extraction** — Full background handling with `yt-dlp` & `ffmpeg`
- 🤖 **Smart AI Formatting** — Headings, bullet points, summaries, and key takeaways
- 🔐 **User Authentication** — Secure signup/login to save and manage notes
- 🌐 **RESTful API Endpoint** — `/generate-Notes/` for background JSON processing
- 🎨 **Modern UI** — Responsive frontend built with Tailwind CSS & HTMX

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Package Manager | [`uv`](https://github.com/astral-sh/uv) |
| Backend | Fastapi |
| Audio Downloader | yt-dlp & ffmpeg |
| Speech-to-Text | Faster-Whisper |
| Generative AI | Google Gemini (`google-genai` SDK) |
| Frontend | HTMX · Tailwind CSS · JavaScript |
| Database | SQLite |

---

## ⚙️ Prerequisites

Make sure the following are installed before you begin:

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)** — lightning-fast Python package manager

  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- **FFmpeg** — required by `yt-dlp` for audio processing

  ```bash
  # macOS
  brew install ffmpeg

  # Linux (Debian/Ubuntu)
  sudo apt install ffmpeg

  # Windows — download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH
  ```

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sairaj-25/yt-ai-Notes.git
cd yt-ai-Notes
```

### 2. Create & Activate a Virtual Environment

```bash
uv venv
```

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (next to `manage.py`):

```env
GEMINI_API_KEY="your_google_gemini_api_key_here"
Fastapi_SECRET_KEY="your_secure_Fastapi_secret_key_here"
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

### 5. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

---

## 🧪 Usage

1. **Sign Up / Log In** — Create an account to access your personal dashboard.
2. **Paste a Link** — Enter any valid YouTube video URL into the input field.
3. **Generate** — Click **Generate**. A loading animation plays while the backend processes the video.
4. **Read & Save** — Your AI-generated notes appear with full formatting, summaries, and key takeaways.

---

## 🗂️ Project Structure

```
**FastAPI Project Structure** (Clean & Professional Version)

```bash
yt-ai-notes/                  # Root folder (Project Name)
├── .env
├── main.py                   # FastAPI entry point
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── .venv/                    # virtual environment
├── app/                      # Main application package
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Settings / configuration
│   │   └── database.py       # Database connection & session
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/               # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── notes.py
│   │   │   │   ├── convert.py
│   │   │   │   └── ... 
│   │   │   └── router.py     # Include all routers
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── note.py
│   │   └── ... 
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── note.py
│   │   └── ...
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── note_service.py
│   │   ├── convert_pdf_service.py
│   │   ├── note_creation_service.py
│   │   └── grammar_audio_transcribe_service.py
│   ├── db/                   # Database related
│   │   ├── __init__.py
│   │   └── schemas.py        # Or migrations folder
│   └── utils/
│       ├── __init__.py
│       ├── pdf_utils.py
│       └── audio_utils.py
├── alembic/                  # (Optional) Database migrations
├── tests/
│   └── ...

```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change, then submit a pull request.

---

## 📄 License

This project is open-source. See the [LICENSE](LICENSE) file for details.
