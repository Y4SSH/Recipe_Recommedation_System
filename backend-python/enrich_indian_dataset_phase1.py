#!/usr/bin/env python3
"""
Phase 1 enrichment for the Indian recipe dataset.

Input schema (Cleaned_Indian_Food_Dataset.csv):
- TranslatedRecipeName
- TranslatedIngredients
- TotalTimeInMins
- Cuisine
- TranslatedInstructions
- URL
- Cleaned-Ingredients
- image-url
- Ingredient-count

Output schema is aligned with recipes_extended.csv (+ variant columns used by this project):
- recipe_title, category, subcategory, ... health_level
- base_recipe, variant_type, cooking_method, protein_type, difficulty_variance

Phase 1 goals:
- Coarse Indian targeting
- Conservative dietary classification
- difficulty, cook_speed, health_level generation
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from ast import literal_eval
from pathlib import Path
from typing import Any, Dict, List


NON_VEG_KEYWORDS = {
    "chicken", "mutton", "lamb", "goat", "beef", "pork", "bacon", "ham",
    "fish", "prawn", "shrimp", "crab", "egg", "eggs", "anchovy",
}

EGG_KEYWORDS = {"egg", "eggs"}

DAIRY_KEYWORDS = {
    "milk", "cream", "paneer", "curd", "yogurt", "yoghurt", "ghee",
    "butter", "cheese", "khoya", "mawa",
}

NUT_KEYWORDS = {
    "almond", "cashew", "pistachio", "walnut", "peanut", "groundnut", "hazelnut",
}

GLUTEN_KEYWORDS = {
    "maida", "wheat", "atta", "semolina", "suji", "rava", "flour", "bread", "noodle",
}

SWEET_KEYWORDS = {"sugar", "jaggery", "honey", "syrup", "condensed milk", "sweet"}
SPICY_KEYWORDS = {"chili", "chilli", "pepper", "garam masala", "red chilli", "green chilli"}
SOUR_KEYWORDS = {"tamarind", "lemon", "lime", "amchur", "vinegar", "yogurt", "curd"}
FRIED_KEYWORDS = {"deep fry", "fry", "fried", "pakora", "bhajiya"}
HEALTHY_KEYWORDS = {"lentil", "dal", "sprout", "vegetable", "millet", "brown rice", "grilled", "steamed"}


def parse_listish(value: Any) -> List[str]:
    if value is None:
        return []

    text = str(value).strip()
    if not text:
        return []

    for parser in (json.loads, literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except Exception:
            pass

    text = text.strip("[]")
    parts = [p.strip(" '\"\t\n\r") for p in text.split(",")]
    return [p for p in parts if p]


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def normalize_token(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def infer_subcategory(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["biryani", "pulao", "rice"]):
        return "rice"
    if any(k in t for k in ["curry", "masala", "korma", "gravy"]):
        return "curry"
    if any(k in t for k in ["roti", "naan", "paratha", "kulcha", "puri"]):
        return "bread"
    if any(k in t for k in ["halwa", "kheer", "barfi", "laddu", "dessert", "sweet"]):
        return "dessert"
    if any(k in t for k in ["chutney", "pickle", "raita"]):
        return "side"
    if any(k in t for k in ["snack", "pakora", "samosa", "chaat", "cutlet"]):
        return "snack"
    return "main"


def infer_course_list(subcategory: str) -> List[str]:
    mapping = {
        "rice": ["main"],
        "curry": ["main"],
        "bread": ["main"],
        "dessert": ["dessert"],
        "side": ["side"],
        "snack": ["snack"],
        "main": ["main"],
    }
    return mapping.get(subcategory, ["main"])


def infer_cuisine_list(cuisine_raw: str, title: str) -> List[str]:
    c = f"{cuisine_raw or ''} {title or ''}".lower()

    if "south" in c or any(x in c for x in ["kerala", "tamil", "andhra", "karnataka", "chettinad"]):
        return ["indian", "south_indian"]
    if "north" in c or any(x in c for x in ["punjabi", "kashmiri", "awadhi", "mughlai"]):
        return ["indian", "north_indian"]
    if "bengal" in c or "bengali" in c:
        return ["indian", "bengali"]
    if "gujarat" in c or "gujarati" in c:
        return ["indian", "gujarati"]
    if "maharashtra" in c or "marathi" in c:
        return ["indian", "maharashtrian"]

    return ["indian"]


def split_time(total_mins: int) -> tuple[int, int]:
    total_mins = max(5, total_mins)
    if total_mins <= 20:
        prep = max(5, round(total_mins * 0.45))
    elif total_mins <= 45:
        prep = max(8, round(total_mins * 0.4))
    else:
        prep = max(10, round(total_mins * 0.35))
    cook = max(1, total_mins - prep)
    return prep, cook


def infer_cook_speed(total_mins: int) -> str:
    if total_mins <= 30:
        return "fast"
    if total_mins <= 60:
        return "medium"
    return "slow"


def split_steps(instructions: str) -> List[str]:
    raw = (instructions or "").replace("\r", "\n")
    parts = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        chunks = re.split(r"(?<=[.!?])\s+|\s*\d+[.)]\s*", line)
        for c in chunks:
            c = c.strip(" -\t")
            if c:
                parts.append(c)
    return parts


def infer_tastes(title: str, ingredients: List[str]) -> tuple[List[str], str, str]:
    text = f"{title} {' '.join(ingredients)}".lower()
    scores = {
        "spicy": sum(1 for k in SPICY_KEYWORDS if k in text),
        "sweet": sum(1 for k in SWEET_KEYWORDS if k in text),
        "sour": sum(1 for k in SOUR_KEYWORDS if k in text),
        "savory": 1,
    }

    tastes = [k for k, v in scores.items() if v > 0]
    tastes_sorted = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = tastes_sorted[0][0]
    secondary = tastes_sorted[1][0] if len(tastes_sorted) > 1 else primary
    return tastes, primary, secondary


def infer_diet_flags(title: str, ingredients: List[str]) -> Dict[str, Any]:
    text = f"{title} {' '.join(ingredients)}".lower()

    has_non_veg = any(k in text for k in NON_VEG_KEYWORDS)
    has_egg = any(k in text for k in EGG_KEYWORDS)
    has_dairy = any(k in text for k in DAIRY_KEYWORDS)
    has_nuts = any(k in text for k in NUT_KEYWORDS)
    has_gluten = any(k in text for k in GLUTEN_KEYWORDS)
    has_pork = any(k in text for k in ["pork", "bacon", "ham"])

    # Conservative classification: uncertain -> False for restrictive labels.
    is_vegan = (not has_non_veg) and (not has_dairy)
    is_vegetarian = (not has_non_veg) and (not has_egg)
    is_halal = not has_pork
    is_kosher = False
    is_nut_free = not has_nuts
    is_dairy_free = not has_dairy
    is_gluten_free = not has_gluten

    profile = []
    if is_vegan:
        profile.append("vegan")
    elif is_vegetarian:
        profile.append("vegetarian")
    else:
        profile.append("non-veg")

    if is_gluten_free:
        profile.append("gluten_free")
    if is_dairy_free:
        profile.append("dairy_free")
    if is_nut_free:
        profile.append("nut_free")
    if is_halal:
        profile.append("halal")

    return {
        "is_vegan": is_vegan,
        "is_vegetarian": is_vegetarian,
        "is_halal": is_halal,
        "is_kosher": is_kosher,
        "is_nut_free": is_nut_free,
        "is_dairy_free": is_dairy_free,
        "is_gluten_free": is_gluten_free,
        "dietary_profile": profile,
    }


def infer_health(title: str, ingredients: List[str], instructions: str, total_mins: int) -> Dict[str, Any]:
    text = f"{title} {' '.join(ingredients)} {instructions}".lower()
    score = 60

    if any(k in text for k in FRIED_KEYWORDS):
        score -= 20
    if any(k in text for k in SWEET_KEYWORDS):
        score -= 8
    if any(k in text for k in ["cream", "butter", "ghee"]):
        score -= 8
    if any(k in text for k in HEALTHY_KEYWORDS):
        score += 12
    if total_mins > 90:
        score -= 3

    score = max(0, min(100, score))

    flags = []
    if any(k in text for k in FRIED_KEYWORDS):
        flags.append("fried")
    if any(k in text for k in ["lentil", "dal", "chana", "rajma", "paneer", "egg", "chicken", "fish"]):
        flags.append("high_protein")
    if any(k in text for k in ["vegetable", "spinach", "palak", "cauliflower", "okra", "beans"]):
        flags.append("veg_rich")

    if score >= 70:
        level = "high"
    elif score >= 45:
        level = "medium"
    else:
        level = "low"

    return {
        "healthiness_score": score,
        "health_flags": list(dict.fromkeys(flags)),
        "health_level": level,
    }


def infer_main_ingredient(ingredients: List[str]) -> str:
    joined = " ".join(ingredients).lower()
    for token in ["chicken", "mutton", "fish", "prawn", "paneer", "lentil", "dal", "potato", "rice"]:
        if token in joined:
            return token
    return normalize_token(ingredients[0]) if ingredients else "unknown"


def infer_difficulty(total_mins: int, num_steps: int, num_ingredients: int) -> str:
    complexity = 0
    complexity += 1 if total_mins > 60 else 0
    complexity += 1 if num_steps > 8 else 0
    complexity += 1 if num_ingredients > 12 else 0

    if complexity <= 0:
        return "easy"
    if complexity == 1:
        return "medium"
    return "hard"


def infer_variant_fields(title: str) -> Dict[str, Any]:
    t = title.lower()
    cooking_method = "standard"
    if any(x in t for x in ["fried", "fry"]):
        cooking_method = "fried"
    elif any(x in t for x in ["baked", "roast"]):
        cooking_method = "baked"
    elif any(x in t for x in ["steam", "steamed"]):
        cooking_method = "steamed"
    elif any(x in t for x in ["pressure", "instant pot", "cooker"]):
        cooking_method = "pressure_cooker"

    variant_type = "standard"
    if "quick" in t:
        variant_type = "quick"
    elif "easy" in t:
        variant_type = "easy"
    elif "traditional" in t:
        variant_type = "traditional"

    protein_type = "vegetarian"
    if any(x in t for x in ["chicken", "mutton", "lamb", "fish", "prawn", "egg"]):
        protein_type = "non_veg"

    base_recipe = re.sub(r"\b(quick|easy|traditional|homestyle|style)\b", "", title, flags=re.IGNORECASE)
    base_recipe = re.sub(r"\s+", " ", base_recipe).strip()

    return {
        "base_recipe": base_recipe or title,
        "variant_type": variant_type,
        "cooking_method": cooking_method,
        "protein_type": protein_type,
        "difficulty_variance": 0,
    }


def enrich_row(row: Dict[str, Any]) -> Dict[str, Any]:
    title = (row.get("TranslatedRecipeName") or "Untitled Recipe").strip()
    description = f"Indian {title}".strip()

    cleaned_ings = parse_listish(row.get("Cleaned-Ingredients"))
    translated_ings = parse_listish(row.get("TranslatedIngredients"))
    ingredients = cleaned_ings or translated_ings
    ingredients = [normalize_token(i) for i in ingredients if normalize_token(i)]

    instructions = (row.get("TranslatedInstructions") or "").strip()
    steps = split_steps(instructions)

    total_mins = max(5, safe_int(row.get("TotalTimeInMins"), 45))
    prep_mins, cook_mins = split_time(total_mins)
    cook_speed = infer_cook_speed(total_mins)

    num_ingredients = safe_int(row.get("Ingredient-count"), len(ingredients) or 1)
    num_steps = len(steps) if steps else max(1, instructions.count(".") + 1)

    subcategory = infer_subcategory(title)
    course_list = infer_course_list(subcategory)
    cuisine_list = infer_cuisine_list(str(row.get("Cuisine") or ""), title)

    tastes, primary_taste, secondary_taste = infer_tastes(title, ingredients)
    diet = infer_diet_flags(title, ingredients)
    health = infer_health(title, ingredients, instructions, total_mins)
    difficulty = infer_difficulty(total_mins, num_steps, num_ingredients)
    main_ingredient = infer_main_ingredient(ingredients)
    variant = infer_variant_fields(title)

    ingredient_text = ", ".join(ingredients)
    directions_text = " ".join(steps) if steps else instructions
    combined_text = f"{title} {ingredient_text} {directions_text}".strip()

    speed_hits = {
        "fast_hits": 1 if cook_speed == "fast" else 0,
        "medium_hits": 1 if cook_speed == "medium" else 0,
        "slow_hits": 1 if cook_speed == "slow" else 0,
    }

    return {
        "recipe_title": title,
        "category": "indian",
        "subcategory": subcategory,
        "description": description,
        "ingredients": json.dumps([{"name": x, "qty": "", "unit": ""} for x in ingredients]),
        "directions": json.dumps(steps if steps else [instructions] if instructions else []),
        "num_ingredients": num_ingredients,
        "num_steps": num_steps,
        "ingredient_text": ingredient_text,
        "directions_text": directions_text,
        "combined_text": combined_text,
        "ingredients_raw": json.dumps(translated_ings if translated_ings else ingredients),
        "directions_raw": instructions,
        "ingredients_canonical": json.dumps(ingredients),
        "cuisine_list": json.dumps(cuisine_list),
        "course_list": json.dumps(course_list),
        "tastes": json.dumps(tastes),
        "primary_taste": primary_taste,
        "secondary_taste": secondary_taste,
        **speed_hits,
        "cook_speed": cook_speed,
        "est_prep_time_min": prep_mins,
        "est_cook_time_min": cook_mins,
        "difficulty": difficulty,
        "is_vegan": str(diet["is_vegan"]).lower(),
        "is_vegetarian": str(diet["is_vegetarian"]).lower(),
        "is_halal": str(diet["is_halal"]).lower(),
        "is_kosher": str(diet["is_kosher"]).lower(),
        "is_nut_free": str(diet["is_nut_free"]).lower(),
        "is_dairy_free": str(diet["is_dairy_free"]).lower(),
        "is_gluten_free": str(diet["is_gluten_free"]).lower(),
        "dietary_profile": json.dumps(diet["dietary_profile"]),
        "healthiness_score": health["healthiness_score"],
        "health_flags": json.dumps(health["health_flags"]),
        "main_ingredient": main_ingredient,
        "health_level": health["health_level"],
        "source_url": row.get("URL") or "",
        "image_url": row.get("image-url") or "",
        **variant,
    }


def enrich_dataset(input_csv: Path, output_csv: Path, sample: int | None = None) -> Dict[str, Any]:
    fieldnames = [
        "recipe_title", "category", "subcategory", "description", "ingredients", "directions",
        "num_ingredients", "num_steps", "ingredient_text", "directions_text", "combined_text",
        "ingredients_raw", "directions_raw", "ingredients_canonical", "cuisine_list", "course_list",
        "tastes", "primary_taste", "secondary_taste", "fast_hits", "slow_hits", "medium_hits",
        "cook_speed", "est_prep_time_min", "est_cook_time_min", "difficulty", "is_vegan",
        "is_vegetarian", "is_halal", "is_kosher", "is_nut_free", "is_dairy_free", "is_gluten_free",
        "dietary_profile", "healthiness_score", "health_flags", "main_ingredient", "health_level",
        "source_url", "image_url",
        "base_recipe", "variant_type", "cooking_method", "protein_type", "difficulty_variance",
    ]

    rows_in = 0
    rows_out = 0

    with input_csv.open("r", encoding="utf-8", newline="") as src, output_csv.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            rows_in += 1
            if sample and rows_out >= sample:
                break
            enriched = enrich_row(row)
            writer.writerow(enriched)
            rows_out += 1

    return {"rows_in": rows_in, "rows_out": rows_out, "output": str(output_csv)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 enrichment for Indian dataset")
    parser.add_argument(
        "--input",
        default="data/Cleaned_Indian_Food_Dataset.csv",
        help="Path to input Indian CSV",
    )
    parser.add_argument(
        "--output",
        default="../indian_enriched_phase1.csv",
        help="Path to output enriched CSV",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Optional sample size for quick validation",
    )

    args = parser.parse_args()

    input_csv = Path(args.input).resolve()
    output_csv = Path(args.output).resolve()

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    stats = enrich_dataset(input_csv, output_csv, sample=args.sample)

    print("=" * 72)
    print("INDIAN DATASET ENRICHMENT (PHASE 1)")
    print("=" * 72)
    print(f"Input:  {input_csv}")
    print(f"Output: {output_csv}")
    print(f"Rows in:  {stats['rows_in']}")
    print(f"Rows out: {stats['rows_out']}")
    print("Completed successfully.")


if __name__ == "__main__":
    main()
