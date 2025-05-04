# 📄 FeedbackLM

A simple Flask web app that improves `.docx` documents using Google's Gemini API.

---

## 🚀 Features

- Upload `.docx` files.
- Improve document content using Gemini.
- Download an improved `.docx` with highlighted changes.
- Simple web UI.

---

## ⚙️ Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/javiercmh/docx-improver.git
   cd docx-improver
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. Install .NET version 8.0. Read [here](https://learn.microsoft.com/en-us/dotnet/core/install/).

4. **Create .env file with Gemini API key** (copy .env.example)
   ```.env
   GEMINI_API_KEY=YOUR_API_KEY_HERE
   ```

5. **Run the app**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 5000
   ```
   - `--reload`: Enables auto-reloading for development. Remove this in production.
   - `--host 0.0.0.0`: Makes the app accessible on your network.
   - `--port 5000`: Specifies the port to run on.
