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

day_index = date.today().toordinal() % len(rows)
entry = rows[day_index]

# --- Text zusammenbauen ---
audio_url = entry["audio_url"]
text = (
    f"Das heutige fantastische Intro kommt aus Folge {entry['id']} "
    f"vom {entry['date']} und wurde von {entry['name']} kreiert. "
    f"Viel Spaß beim Hören! 🎧\n{audio_url}"
)

# --- Link-Position im Text berechnen (als UTF-8 Bytes) ---
text_bytes = text.encode("utf-8")
url_bytes = audio_url.encode("utf-8")
link_start = text_bytes.index(url_bytes)
link_end = link_start + len(url_bytes)

print("Textlänge:", len(text))
print("Text:", text)

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
            "facets": [
                {
                    "index": {
                        "byteStart": link_start,
                        "byteEnd": link_end
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#link",
                            "uri": audio_url
                        }
                    ]
                }
            ]
        }
    }
)
print("Status:", post.status_code)
print("Antwort:", post.text)
post.raise_for_status()
print("✅ Erfolgreich gepostet!")
