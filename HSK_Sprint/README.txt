HSK 1 Sprint

Option A (offline, no Docker): open site/index.html in a browser.

Option B (Docker, on your Mac mini):
  cd HSK_Sprint
  docker compose up -d --build
  Open http://<mac-mini-or-tailscale-name>:8088

Change the port in docker-compose.yml ("8088:80"), then run: docker compose up -d
Stop: docker compose down

Notes
- Progress is stored in each browser, per address and port. Always use the same URL
  on a device, or your progress will look empty. Settings has a backup/restore.
- Audio uses the device's own Chinese voice.
- Nicer Chinese font loads from Google Fonts when online; offline it falls back to the system font.
