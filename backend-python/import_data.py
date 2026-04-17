import argparse
import csv
import json
import uuid
from ast import literal_eval
from pathlib import Path
from typing import Any, List
from time import perf_counter
from sqlalchemy import text

from app.database import SessionLocal, engine, Base
from app.models import Recipe, SavedRecipe, Rating, Feedback


# Ensure tables exist.
Base.metadata.create_all(bind=engine)


def parse_jsonish_list(raw_value: Any) -> List[str]:
    if raw_value is None:
        return []

    text = str(raw_value).strip()
    if not text:
        return []

    for parser in (json.loads, literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except Exception:
            pass

    return [part.strip() for part in text.split(",") if part.strip()]


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def build_ingredients(items: List[str]) -> List[dict]:
    return [{"name": item.lower(), "qty": "", "unit": ""} for item in items]


def import_extended_csv(csv_path: str, batch_size: int = 2000) -> None:
    started = perf_counter()
    db = SessionLocal()
    try:
        # Replace recipe corpus and dependent recipe interactions.
        db.query(SavedRecipe).delete()
        db.query(Rating).delete()
        db.query(Feedback).delete()
        db.query(Recipe).delete()
        db.commit()

        count = 0
        batch_rows = []

        # Import optimization for large datasets.
        db.execute(text("PRAGMA synchronous = OFF"))
        db.execute(text("PRAGMA journal_mode = WAL"))

        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                title = (row.get("recipe_title") or "Untitled Recipe").strip()
                description = (row.get("description") or "").strip() or None

                ingredients_list = parse_jsonish_list(row.get("ingredients_raw") or row.get("ingredients"))
                steps_list = parse_jsonish_list(row.get("directions_raw") or row.get("directions"))
                main_ingredients = parse_jsonish_list(row.get("ingredients_canonical"))
                if not main_ingredients:
                    main_ingredients = ingredients_list[:15]

                cuisine_list = parse_jsonish_list(row.get("cuisine_list"))
                course_list = parse_jsonish_list(row.get("course_list"))
                tastes = parse_jsonish_list(row.get("tastes"))
                dietary_profile = parse_jsonish_list(row.get("dietary_profile"))

                tags = [
                    *(t for t in [row.get("category"), row.get("subcategory")] if t),
                    *cuisine_list,
                    *course_list,
                    *tastes,
                    *dietary_profile,
                ]

                health_flags = parse_jsonish_list(row.get("health_flags"))
                nutrition = {
                    "healthiness_score": to_int(row.get("healthiness_score"), 0),
                    "health_level": row.get("health_level") or "unknown",
                    "health_flags": health_flags,
                    "dietary_profile": dietary_profile,
                }

                prep_time = to_int(row.get("est_prep_time_min"), 10)
                cook_time = to_int(row.get("est_cook_time_min"), 20)
                total_time = max(1, prep_time + cook_time)

                # Extract variant tagging fields (if available)
                base_recipe = (row.get("base_recipe") or "").strip() or None
                variant_type = (row.get("variant_type") or "").strip() or None
                cooking_method = (row.get("cooking_method") or "").strip() or None
                protein_type = (row.get("protein_type") or "").strip() or None
                difficulty_variance = row.get("difficulty_variance")
                try:
                    difficulty_variance = int(float(difficulty_variance)) if difficulty_variance else None
                except (ValueError, TypeError):
                    difficulty_variance = None

                recipe_row = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "description": description,
                    "ingredients": json.dumps(build_ingredients(ingredients_list)),
                    "steps": json.dumps(steps_list),
                    "cuisine": (cuisine_list[0] if cuisine_list else (row.get("category") or "global")),
                    "tags": json.dumps(list(dict.fromkeys([str(tag).strip().lower() for tag in tags if str(tag).strip()]))),
                    "cook_time": cook_time,
                    "prep_time": prep_time,
                    "total_time": total_time,
                    "servings": 4,
                    "difficulty": (row.get("difficulty") or "medium").strip().lower(),
                    "nutrition": json.dumps(nutrition),
                    "image_url": None,
                    "source_url": None,
                    "created_by": "recipes_extended.csv",
                    "main_ingredients": json.dumps([m.lower() for m in main_ingredients]),
                    # Variant tagging fields
                    "base_recipe": base_recipe,
                    "variant_type": variant_type,
                    "cooking_method": cooking_method,
                    "protein_type": protein_type,
                    "difficulty_variance": difficulty_variance,
                }

                batch_rows.append(recipe_row)
                count += 1

                if len(batch_rows) >= max(200, batch_size):
                    db.bulk_insert_mappings(Recipe, batch_rows)
                    batch_rows.clear()
                    db.commit()
                    print(f"Imported {count} recipes...")

            if batch_rows:
                db.bulk_insert_mappings(Recipe, batch_rows)

        db.commit()
        elapsed = perf_counter() - started
        speed = (count / elapsed) if elapsed > 0 else 0
        print(f"Import completed. Total recipes imported: {count}")
        print(f"Time taken: {elapsed:.2f}s ({speed:.1f} recipes/sec)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import recipes into recipes.db")
    parser.add_argument(
        "--csv",
        default="../recipes_extended.csv",
        help="Path to recipes CSV file (default: ../recipes_extended.csv)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2000,
        help="Rows per insert batch for faster large imports (default: 2000)",
    )
    args = parser.parse_args()

    csv_file = Path(args.csv).resolve()
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV not found: {csv_file}")

    import_extended_csv(str(csv_file), batch_size=args.batch_size)