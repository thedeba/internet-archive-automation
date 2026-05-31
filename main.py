from internetarchive import configure, upload, get_item
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
import os
import re
import json
import time
import sys

load_dotenv()

USERNAME     = os.environ["IA_USERNAME"]
PASSWORD     = os.environ["IA_PASSWORD"]
PDF_DIR      = os.environ.get("PDF_DIR", "pdf")   # folder to scan for PDFs
JSONL_OUTPUT = "uploads.jsonl"
DELAY_SEC    = int(os.environ.get("DELAY_SEC", "30"))  # seconds between uploads

# ── Authenticate once ──────────────────────────────────────────────────────────
print("Authenticating with Internet Archive...")
try:
    configure(username=USERNAME, password=PASSWORD)
    print("Credentials configured ✅\n")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    sys.exit(1)

# ── Collect PDFs to upload ─────────────────────────────────────────────────────
pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))

if not pdf_files:
    print(f"No PDF files found in '{PDF_DIR}/'")
    sys.exit(0)

# Skip files already recorded in the JSONL (resume support)
already_uploaded = set()
if Path(JSONL_OUTPUT).exists():
    with open(JSONL_OUTPUT, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            already_uploaded.add(record.get("title", ""))

print(f"Found {len(pdf_files)} PDF(s). {len(already_uploaded)} already uploaded.\n")

# ── Upload loop ────────────────────────────────────────────────────────────────
for i, pdf_path in enumerate(pdf_files):
    stem       = pdf_path.stem
    title      = stem
    description = stem
    subject    = stem
    identifier = re.sub(r'[^a-zA-Z0-9]+', '-', stem).strip('-').lower()

    if title in already_uploaded:
        print(f"[{i+1}/{len(pdf_files)}] Skipping '{title}' (already in uploads.jsonl)")
        continue

    print(f"[{i+1}/{len(pdf_files)}] Checking: {title}")
    print(f"  Identifier : {identifier}")

    # ── Check if item already exists on archive.org ────────────────────────
    def save_link():
        pdf_link = f"https://archive.org/download/{identifier}/{quote(pdf_path.name)}"
        record   = {"title": title, "link": pdf_link}
        with open(JSONL_OUTPUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"  📄 Saved to {JSONL_OUTPUT}: {pdf_link}")
        return pdf_link

    try:
        item = get_item(identifier)
        if item.exists:
            print(f"  ℹ️  Already exists on archive.org — saving link without re-uploading.")
            save_link()
            print()
            continue
    except Exception:
        pass  # If we can't check, proceed to upload

    print(f"  File       : {pdf_path}")
    try:
        responses = upload(
            identifier,
            files=[str(pdf_path)],
            metadata={
                'title':       title,
                'description': description,
                'subject':     subject,
                'mediatype':   'texts',
            },
            verbose=True,
            retries=3,
            retries_sleep=15,
        )

        success = all(r.status_code in (200, 201) for r in responses)

        if success:
            link = save_link()
            print(f"  ✅ Upload successful! PDF link: {link}\n")
        else:
            for r in responses:
                if r.status_code not in (200, 201):
                    print(f"  ❌ HTTP {r.status_code}: {r.text[:300]}\n")

    except Exception as e:
        err = str(e)
        if "SlowDown" in err or "spam" in err.lower() or "reduce your request rate" in err.lower():
            print(f"  ⛔ Account rate-limited or flagged as spam.")
            print(f"     → Email info@archive.org to unblock, or use a different account.\n")
            sys.exit(1)
        else:
            print(f"  ❌ Upload failed: {e}\n")

    # Pause between uploads to avoid triggering rate limits
    if i < len(pdf_files) - 1:
        remaining = [p for p in pdf_files[i+1:] if p.stem not in already_uploaded]
        if remaining:
            print(f"  ⏳ Waiting {DELAY_SEC}s before next upload...\n")
            time.sleep(DELAY_SEC)

print("All done!")
