"""
Gmail API client — handles all Gmail operations via OAuth2 (Desktop App credentials).

Usage:
    python3 execution/gmail_client.py auth
    python3 execution/gmail_client.py fetch "from:company" 5
    python3 execution/gmail_client.py list_drafts 10
    python3 execution/gmail_client.py create_draft '{"to":"a@b.com","subject":"Hi","body":"Hello","is_html":true}'
    python3 execution/gmail_client.py delete_draft DRAFT_ID
    python3 execution/gmail_client.py get_email MESSAGE_ID

Setup:
    1. Create a Google Cloud project and enable the Gmail API
    2. Create OAuth2 Desktop App credentials
    3. Download credentials.json to the project root
    4. Run: python3 execution/gmail_client.py auth
    5. Complete the OAuth flow in your browser
    6. token.json will be created automatically

Dependencies:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import sys
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://mail.google.com/"]
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"


def get_service():
    """Authenticate and return a Gmail API service instance."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"ERROR: {CREDENTIALS_FILE} not found. Download it from Google Cloud Console.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_emails(query: str, max_results: int = 10) -> list:
    """Search emails by Gmail query string. Returns list of message dicts."""
    service = get_service()
    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = result.get("messages", [])
    output = []
    for msg_stub in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_stub["id"], format="full"
        ).execute()
        output.append(_parse_message(msg))
    return output


def get_email(message_id: str) -> dict:
    """Get a single email by message ID."""
    service = get_service()
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()
    return _parse_message(msg)


def list_drafts(max_results: int = 10) -> list:
    """List Gmail drafts. Returns list of draft dicts."""
    service = get_service()
    result = service.users().drafts().list(
        userId="me", maxResults=max_results
    ).execute()
    drafts = result.get("drafts", [])
    output = []
    for d in drafts:
        draft = service.users().drafts().get(
            userId="me", id=d["id"], format="full"
        ).execute()
        msg = draft.get("message", {})
        parsed = _parse_message(msg)
        parsed["draft_id"] = draft["id"]
        output.append(parsed)
    return output


def create_draft(to: str, subject: str, body: str,
                 is_html: bool = False, thread_id: str = None) -> dict:
    """Create a Gmail draft. Returns draft metadata."""
    service = get_service()
    if is_html:
        message = MIMEMultipart("alternative")
        message["to"] = to
        message["subject"] = subject
        message.attach(MIMEText(body, "html"))
    else:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    draft = service.users().drafts().create(
        userId="me", body=draft_body
    ).execute()

    return {
        "draft_id": draft["id"],
        "message_id": draft["message"]["id"],
        "thread_id": draft["message"].get("threadId", ""),
    }


def delete_draft(draft_id: str) -> bool:
    """Delete a Gmail draft by draft ID."""
    service = get_service()
    service.users().drafts().delete(userId="me", id=draft_id).execute()
    return True


def _parse_message(msg: dict) -> dict:
    """Extract useful fields from a raw Gmail API message."""
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body_text = _extract_body(msg.get("payload", {}))
    attachments = _extract_attachments(msg.get("payload", {}))
    return {
        "id": msg.get("id", ""),
        "threadId": msg.get("threadId", ""),
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "date": headers.get("date", ""),
        "body": body_text,
        "attachments": attachments,
        "labels": msg.get("labelIds", []),
    }


def _extract_body(payload: dict, prefer_html: bool = False) -> str:
    """Recursively extract text body from message payload."""
    mime = payload.get("mimeType", "")

    if mime == "text/plain" and not prefer_html:
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime == "text/html":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    parts = payload.get("parts", [])
    texts = []
    for part in parts:
        result = _extract_body(part, prefer_html)
        if result:
            texts.append(result)
    return texts[0] if texts else ""


def _extract_attachments(payload: dict) -> list:
    """Extract attachment filenames from message payload."""
    attachments = []
    parts = payload.get("parts", [])
    for part in parts:
        filename = part.get("filename", "")
        if filename:
            attachments.append(filename)
        attachments.extend(_extract_attachments(part))
    return attachments


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "auth":
        get_service()
        print("Authenticated successfully. token.json created/refreshed.")

    elif cmd == "fetch":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        max_r = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = fetch_emails(query, max_r)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif cmd == "list_drafts":
        max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        results = list_drafts(max_r)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif cmd == "create_draft":
        data = json.loads(sys.argv[2])
        result = create_draft(
            to=data["to"],
            subject=data["subject"],
            body=data["body"],
            is_html=data.get("is_html", False),
            thread_id=data.get("thread_id"),
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "delete_draft":
        draft_id = sys.argv[2]
        delete_draft(draft_id)
        print(f"Draft {draft_id} deleted.")

    elif cmd == "get_email":
        msg_id = sys.argv[2]
        result = get_email(msg_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
