# Internet Archive PDF Automation

A robust and efficient Python utility designed to automate uploading PDF collections directly to the **Internet Archive** (archive.org) using their official S3-based API.

## Features

- **Folder Scanning:** Automatically detects all PDF files within a designated folder (defaults to `pdf/`).
- **Official S3 API Integration:** Utilizes the official `internetarchive` Python client for high-speed, direct uploads instead of slow and fragile browser automation.
- **Smart Resume & Skip:** 
  1. Checks `uploads.jsonl` to skip already-logged items.
  2. Queries the Internet Archive (`get_item()`) before uploading to see if the identifier already exists. If it exists, it saves the direct PDF link to the logs and skips the upload.
- **Percent-Encoded URLs:** Automatically percent-encodes generated download URLs (e.g., spaces converted to `%20`) so saved links are immediately usable.
- **Rate-Limit & Anti-Spam Safeguards:** Implements configurable polite delays (`DELAY_SEC`) between consecutive uploads and exits gracefully if account limits or spam flags are triggered.
- **Local Progress Tracking:** Appends successful uploads as JSON lines in `uploads.jsonl` containing the `title` and direct download `link`.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thedeba/internet-archive-automation.git
   cd internet-archive-automation
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your Internet Archive credentials and preferences:
   ```env
   IA_USERNAME=your_email@gmail.com
   IA_PASSWORD=your_password
   PDF_DIR=pdf
   DELAY_SEC=30
   ```

---

## How to Use

1. Put all your PDF files inside the `pdf/` folder.
2. Activate your virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Run the automation script:
   ```bash
   python main.py
   ```

Upon completion, all successfully uploaded files (or previously uploaded files verified via the API) will be recorded in `uploads.jsonl`:
```json
{"title": "HSTU Admission 2026", "link": "https://archive.org/download/hstu-admission-2026/HSTU%20Admission%202026.pdf"}
```

---

## Troubleshooting

- **Account Flagged / Spam Error:**
  If you see an error like `Your upload of ... appears to be spam`, it is a block enforced at the account level by archive.org (often triggered by using temporary email domains or rapid uploads on new accounts). 
  - To resolve, register an account with a legitimate email provider (e.g., Gmail) or contact `info@archive.org` with the spam `RequestId` to clear the flag.
