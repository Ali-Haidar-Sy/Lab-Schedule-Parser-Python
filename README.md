# 🎓 University Schedule Emulator (Generic CLI Tool)

<p align="center">
  <a href="https://www.instagram.com/_UNGN"><img src="https://img.shields.io/badge/Instagram-%23E4405F.svg?style=for-the-badge&logo=Instagram&logoColor=white" alt="Instagram"></a>
  <a href="https://github.com/Ali-Haidar-Sy"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://t.me/P33_9"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
</p>

<p align="center">
  <em>Automate fetching and searching of academic schedules from any university’s LMS that uses CSRF‑protected APIs + JSON data.</em>
</p>

---

## ✨ Features

- 🔐 **Generic CSRF login handler** – adapt to your university’s authentication flow
- 📅 **Fetches schedule for any date range** (monthly view by default)
- 🧹 **HTML‑to‑text cleaning** – removes tags from descriptions
- 🔍 **Three search modes** (fully customizable):
  - By **day** (e.g., `28.03.2026`)
  - By **subject** name
  - By **teacher** name
- 📌 **Detailed output** – time, lesson type, teacher, room, group, direct link
- 🚀 **Lightweight** – uses only `requests` + `BeautifulSoup`

> ⚠️ **This is a template.** The original code was built for a specific university (`lk.sangtu.ru`). You **must** modify the URLs, login logic, and JSON parsing to match your own institution’s LMS.

---

## ⚠️ Critical – You MUST Update Credentials & Endpoints

The code contains **hardcoded placeholders** for:
- `USERNAME` / `PASSWORD`
- `LOGIN_URL` / `API_URL`

**Before running, you MUST:**

1. Replace the login URL with your university’s authentication endpoint.
2. Replace the API URL with the endpoint that returns schedule data in JSON.
3. Provide your real credentials **securely** (never commit them).

**Recommended secure method (environment variables):**

```python
import os
USERNAME = os.environ.get("UNI_USERNAME")
PASSWORD = os.environ.get("UNI_PASSWORD")
