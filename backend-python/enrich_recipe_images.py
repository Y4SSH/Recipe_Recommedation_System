import argparse
import json
import time
import urllib.parse
import urllib.request

from app.database import SessionLocal
from app.models import Recipe


WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"


def fetch_wikimedia_thumbnail(recipe_title: str, timeout: float = 4.0):
    query = f"{recipe_title} food"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "1",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "640",
    }
    url = f"{WIKIMEDIA_API}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(url, headers={"User-Agent": "RecipeRecommender/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
    except Exception:
        return None

    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        thumb = info.get("thumburl")
        original = info.get("url")
        return thumb or original

    return None


def enrich_images(limit: int, sleep_ms: int):
    db = SessionLocal()
    updated = 0
    checked = 0
    delay = max(0, sleep_ms) / 1000.0

    try:
        recipes = (
            db.query(Recipe)
            .filter((Recipe.image_url.is_(None)) | (Recipe.image_url == ""))
            .limit(limit)
            .all()
        )

        for recipe in recipes:
            checked += 1
            image_url = fetch_wikimedia_thumbnail(recipe.title)
            if image_url:
                recipe.image_url = image_url
                recipe.source_url = "wikimedia:commons"
                updated += 1

            if checked % 50 == 0:
                db.commit()
                print(f"Checked {checked}, updated {updated}")

            if delay > 0:
                time.sleep(delay)

        db.commit()
        print(f"Image enrichment done. Checked: {checked}, updated: {updated}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich recipe images via Wikimedia Commons")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum recipes to process")
    parser.add_argument("--sleep-ms", type=int, default=50, help="Delay between requests in ms")
    args = parser.parse_args()

    enrich_images(limit=args.limit, sleep_ms=args.sleep_ms)
