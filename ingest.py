"""Pull Steam game details + player reviews, store them in SQLite (structured)
and ChromaDB (semantic search). Run once: python ingest.py"""
import sqlite3
import time

import chromadb
import requests

# Verify these app IDs on each game's Steam store URL; swap in any games you like.
GAMES = {
    1172470: "Apex Legends",
    1517290: "Battlefield 2042",
    1426210: "It Takes Two",
    1245620: "Elden Ring",
    1091500: "Cyberpunk 2077",
    1086940: "Baldur's Gate 3",
}
PAGES_PER_GAME = 5          # 100 reviews per page
DB_PATH = "games.db"
CHROMA_PATH = "chroma_db"


def fetch_details(appid):
    r = requests.get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid}, timeout=30,
    )
    data = r.json().get(str(appid), {})
    if not data.get("success"):
        return {}
    return data["data"]


def fetch_reviews(appid):
    reviews, cursor = [], "*"
    for _ in range(PAGES_PER_GAME):
        r = requests.get(
            f"https://store.steampowered.com/appreviews/{appid}",
            params={
                "json": 1, "filter": "recent", "language": "english",
                "num_per_page": 100, "purchase_type": "all", "cursor": cursor,
            },
            timeout=30,
        )
        payload = r.json()
        batch = payload.get("reviews", [])
        if not batch:
            break
        reviews.extend(batch)
        new_cursor = payload.get("cursor")
        if not new_cursor or new_cursor == cursor:
            break
        cursor = new_cursor
        time.sleep(1)  # be polite to the API
    return reviews


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        DROP TABLE IF EXISTS games;
        DROP TABLE IF EXISTS reviews;
        CREATE TABLE games (appid INTEGER PRIMARY KEY, name TEXT, genres TEXT,
                            price_usd REAL, release_date TEXT);
        CREATE TABLE reviews (id TEXT PRIMARY KEY, appid INTEGER, voted_up INTEGER,
                              playtime_hours REAL, votes_up INTEGER,
                              created TEXT, text TEXT);
        """
    )

    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        chroma.delete_collection("reviews")
    except Exception:
        pass
    col = chroma.create_collection("reviews")

    for appid, name in GAMES.items():
        print(f"Fetching {name}...")
        d = fetch_details(appid)
        genres = ", ".join(g["description"] for g in d.get("genres", []))
        price = (d.get("price_overview", {}).get("final", 0) or 0) / 100
        conn.execute(
            "INSERT OR REPLACE INTO games VALUES (?,?,?,?,?)",
            (appid, name, genres, price, d.get("release_date", {}).get("date", "")),
        )

        ids, docs, metas = [], [], []
        for rv in fetch_reviews(appid):
            text = (rv.get("review") or "").strip()
            if len(text) < 40:      # skip empty / one-word reviews
                continue
            rid = str(rv["recommendationid"])
            hours = round(rv["author"].get("playtime_forever", 0) / 60, 1)
            created = time.strftime("%Y-%m-%d", time.gmtime(rv["timestamp_created"]))
            conn.execute(
                "INSERT OR REPLACE INTO reviews VALUES (?,?,?,?,?,?,?)",
                (rid, appid, int(rv["voted_up"]), hours, rv.get("votes_up", 0), created, text),
            )
            ids.append(rid)
            docs.append(text[:1500])
            metas.append({"appid": appid, "game": name,
                          "voted_up": bool(rv["voted_up"]), "playtime_hours": hours})

        for i in range(0, len(ids), 200):
            col.add(ids=ids[i:i + 200], documents=docs[i:i + 200], metadatas=metas[i:i + 200])
        print(f"  stored {len(ids)} reviews")

    conn.commit()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
