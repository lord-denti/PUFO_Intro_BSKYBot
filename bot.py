import csv
import os
import requests
from datetime import date

HANDLE = os.environ["BSKY_HANDLE"]
PASSWORD = os.environ["BSKY_PASSWORD"]

# --- Login ---
resp = requests.post("https://bsky.social/xrpc/com.atproto.server.createSession",
    json={"identifier": HANDLE, "password": PASSWORD})
resp.raise_for_status()
session = resp.json()
token = session["accessJwt"]
did = session["did"]

# --- CSV lesen & heutigen Eintrag wählen ---
with open("intros.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Nimm den Eintrag des Tages (rotierend durch die Liste)
day_index = date.today().toordinal() % len(rows)
entry = rows[day_index]

# --- Text zusammenbauen ---
audio_url = entry["audio_url"]
text = (
    f"Das fantastische Intro heute stammt aus Folge {entry['id']}, ",
    f"erschienen am {entry['date']}, und wurde von {entry['name']} gemacht. "
    f"Viel Spaß beim Hören! 🎧\n{audio_url}"
)

# --- Auf Bluesky posten ---
post = requests.post(
    "https://bsky.social/xrpc/com.atproto.repo.createRecord",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": date.today().isoformat() + "T12:00:00Z",
        }
    }
)
post.raise_for_status()
print("✅ Erfolgreich gepostet:", text)
