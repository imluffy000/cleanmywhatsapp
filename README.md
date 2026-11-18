# CleanMyWhatsApp

**Your WhatsApp is eating your phone. Take the storage back — safely.**

WhatsApp media is the #1 storage hog on most Android phones: gigabytes of forwarded
videos, duplicate images, and status downloads you never asked to keep. Nobody cleans
it because nobody knows what is safe to remove.

CleanMyWhatsApp is not an app. It is a guided cleanup you run with an AI coding
assistant (Claude Code, Codex, or Gemini CLI) and Android's own debug bridge (ADB):

1. **Scan** — the assistant inventories your WhatsApp media over ADB and classifies it:
   exact duplicates (hash-verified), status downloads, your own "Sent" copies,
   large videos, and old media.
2. **Report** — you get a clear report: how much each category holds and how much
   you would recover. Nothing has been touched yet.
3. **Approve** — you pick the categories (or individual files). The assistant never
   acts on anything you did not approve.
4. **Back up, then clean** — approved files are first copied to your computer, and
   only then removed from the phone. A restore script can put everything back.

No root. No uninstalling. No file is deleted before a verified backup copy exists
on your computer.

## Requirements

- An Android phone with WhatsApp (USB debugging enabled — the prompt walks you
  through it)
- A computer on the same desk (USB cable) or same Wi-Fi (ADB over Wi-Fi)
- An AI coding assistant that can run shell commands

## Quick start

```bash
git clone https://github.com/imluffy000/cleanmywhatsapp
cd cleanmywhatsapp
# Open this folder in your coding assistant and paste the prompt from PROMPT.md
```

## Safety rules (non-negotiable, enforced by PROMPT.md)

- Backup before delete, always. The backup is verified (file count + total size)
  before a single file is removed from the phone.
- Nothing outside WhatsApp media folders is ever touched.
- Chats, databases, and documents are out of scope for v0.1 — media only.
- Every run writes a log; `restore` puts everything back from the backup.

## Status

v0.1 in development. The scan + report step works today; backup/clean/restore
are being hardened before the first tagged release.

## License

MIT
