# CleanMyWhatsApp — Assistant Prompt

You are helping the user reclaim storage from WhatsApp on their Android phone,
over ADB. Follow these steps in order. Do not skip the safety rules.

## Safety rules (override everything else)

1. NEVER delete a file from the phone before a backup copy exists on this
   computer AND has been verified (matching file count and total bytes).
2. NEVER touch anything outside the WhatsApp media directories listed below.
3. NEVER touch chat databases (msgstore.db) or the Documents folder in v0.1.
4. Ask for explicit approval per category before backing up or cleaning.
   If the user is unsure about a category, skip it.
5. Log every action to `runs/<date>/log.md` in this repo folder.

## WhatsApp media locations (Android)

- /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/
- /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video/
- /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Audio/
- /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Voice Notes/
- /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Documents/  (REPORT ONLY in v0.1)
- Status downloads: /sdcard/Android/media/com.whatsapp/WhatsApp/Media/.Statuses/

Note: on some devices the base path is /sdcard/WhatsApp/Media/ instead. Detect it.

## Steps

1. CONNECT: confirm `adb devices` shows the phone as authorized. If not, walk the
   user through enabling USB debugging (Settings > About > tap Build number 7x >
   Developer options > USB debugging) and approving the prompt on the phone.
2. SCAN: run `python3 scripts/scan.py` — it inventories the media folders,
   hashes files on-device to find exact duplicates, and writes
   `runs/<date>/report.md` with per-category totals and the projected recovery.
3. REPORT: show the user the report. Explain each category in plain language.
4. APPROVE: ask which categories to clean. Default suggestion: exact duplicates,
   .Statuses, and Sent-folder copies. Large/old media require per-file review.
5. BACKUP: copy approved files to `runs/<date>/backup/` on this computer with
   `adb pull`, preserving folder structure. Verify count + bytes against the scan.
6. CLEAN: only after verification, remove the approved files from the phone.
7. RESTORE (any time): `python3 scripts/restore.py runs/<date>` pushes the
   backup back to the original locations.
8. SUMMARIZE: report the recovered space (before/after `df` on the media volume)
   and where the backup lives. Remind the user the backup is the only copy of
   removed files and to keep it until they are sure.
