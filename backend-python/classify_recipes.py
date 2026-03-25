import json
from app.database import SessionLocal
from app.models import Recipe
from app.food_classifier import classify_veg_nonveg


def safe_parse_list(value: str):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(v).strip().lower() for v in parsed if str(v).strip()]
    except Exception:
        pass
    return [x.strip().lower() for x in str(value).split(',') if x.strip()]


def main():
    db = SessionLocal()
    try:
        recipes = db.query(Recipe).all()
        veg_count = 0
        non_veg_count = 0

        for recipe in recipes:
            main_ings = safe_parse_list(recipe.main_ingredients)
            full_ings = []
            try:
                parsed = json.loads(recipe.ingredients or "[]")
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and "name" in item:
                            full_ings.append(str(item["name"]).strip().lower())
                        elif isinstance(item, str):
                            full_ings.append(item.strip().lower())
            except Exception:
                pass

            all_ings = list(dict.fromkeys(main_ings + full_ings))
            category = classify_veg_nonveg(all_ings)

            tags = safe_parse_list(recipe.tags)
            tags = [t for t in tags if t not in ("veg", "non-veg")]
            tags.append(category)
            recipe.tags = json.dumps(sorted(set(tags)))

            if category == "veg":
                veg_count += 1
            else:
                non_veg_count += 1

        db.commit()
        print(f"Updated {len(recipes)} recipes")
        print(f"Veg: {veg_count}")
        print(f"Non-veg: {non_veg_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
