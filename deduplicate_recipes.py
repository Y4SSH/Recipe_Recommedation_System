import csv
import re
from pathlib import Path

csv_path = 'd:\\Projects\\Major-Project\\recipes_extended.csv'
output_path = 'd:\\Projects\\Major-Project\\recipes_extended_deduplicated.csv'

def normalize_recipe_title(title):
    """
    Remove common modifiers to get base recipe name.
    Examples:
    - "Air Fryer Samosa" -> "samosa"
    - "Beef Tacos" -> "tacos"
    - "Mini Sweet Potato Samosa" -> "sweet potato samosa"
    """
    if not title:
        return ""
    
    # Modifiers to remove
    modifiers = [
        r'\b(air fryer|instant pot|slow cooker|crockpot|oven|stovetop|grilled?|baked?|fried?|roasted?)\b',
        r'\b(homemade|easy|quick|simple|classic|traditional|authentic)\b',
        r'\b(mini|small|large|giant|big|tiny)\b',
        r'\b(ground|chopped|diced|sliced|whole|cut|cubed)\b',
        r'\b(beef|chicken|pork|fish|salmon|tuna|shrimp|prawn|lamb|venison|turkey|duck)\b',
        r'\b(vegetarian|vegan|gluten.?free)\b',
        r'\b(spicy|mild|sweet|savory|sour|tangy)\b',
        r'\b(low.?carb|keto|paleo|sugar.?free|fat.?free|light|healthy)\b',
    ]
    
    normalized = title.lower().strip()
    for pattern in modifiers:
        normalized = re.sub(pattern, ' ', normalized, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def make_comparable_key(recipe):
    """
    Create a key for detecting exact duplicates.
    Uses title, main ingredients, and directions.
    """
    title = (recipe.get('recipe_title') or '').strip().lower()
    ingredients = (recipe.get('ingredients_raw') or recipe.get('ingredients') or '').lower()[:100]
    directions = (recipe.get('directions_raw') or recipe.get('directions') or '').lower()[:100]
    return (title, ingredients, directions)

# Read all recipes
print("Reading recipes...")
all_recipes = []
with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_recipes.append(row)

print(f"Total recipes before dedup: {len(all_recipes)}")

# Step 1: Remove exact duplicates
print("Removing exact duplicates...")
seen_exact = set()
after_exact_dedup = []
for recipe in all_recipes:
    key = make_comparable_key(recipe)
    if key not in seen_exact:
        seen_exact.add(key)
        after_exact_dedup.append(recipe)

print(f"After removing exact duplicates: {len(after_exact_dedup)}")

# Step 2: Remove variants (keep only one per normalized base title)
print("Removing recipe variants...")
seen_normalized = {}
after_variant_dedup = []
for recipe in after_exact_dedup:
    title = recipe.get('recipe_title', '').strip()
    normalized = normalize_recipe_title(title)
    
    if normalized and normalized not in seen_normalized:
        seen_normalized[normalized] = title
        after_variant_dedup.append(recipe)

print(f"After removing variants: {len(after_variant_dedup)}")
print(f"Total removed: {len(all_recipes) - len(after_variant_dedup)} recipes")

# Step 3: Write deduplicated CSV
print(f"Writing deduplicated CSV to: {output_path}")
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    if after_variant_dedup:
        writer = csv.DictWriter(f, fieldnames=after_variant_dedup[0].keys())
        writer.writeheader()
        writer.writerows(after_variant_dedup)

print(f"\nDone! New dataset: {len(after_variant_dedup)} recipes")
print(f"Reduction: {len(all_recipes)} -> {len(after_variant_dedup)} ({100 * (1 - len(after_variant_dedup)/len(all_recipes)):.1f}% removed)")
