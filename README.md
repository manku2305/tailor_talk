# 🧵 TailorTalk – AI Meeting Scheduler

TailorTalk is a smart assistant that helps users:
- 🧠 Understand natural language requests
- 🗓️ Check calendar availability (via Google Calendar)
- 📅 Book meetings with smart time parsing
- 💬 Respond intelligently, even without GPT access

---

## 🔧 Features

- ✅ Accepts natural language input (e.g., “Book a meeting tomorrow at 4pm”)
- ✅ Uses LangGraph to route the conversation
- ✅ Classifies user intent: booking vs. checking availability
- ✅ Parses time intelligently using regex + `dateparser`
- ✅ Checks availability using Google Calendar API
- ✅ Books real meetings and returns calendar links

---

## 🚀 Installation

1. Clone the repo or download the folder
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # on macOS/Linux
    venv\Scripts\activate     # on Windows
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Add your `.env` file in the root directory:

    ```env
    OPENAI_API_KEY=your_openai_key_here
    ```

5. Set up Google Calendar:
   - Go to https://console.cloud.google.com/
   - Create a project and enable **Google Calendar API**
   - Download `credentials.json` and place it in `calendar_utils/`
   - On first run, a browser will open to authenticate

---

## 🖥️ Running the App

### Backend (FastAPI):
```bash
uvicorn backend.main:app --reload
