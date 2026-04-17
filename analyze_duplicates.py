import csv
from collections import defaultdict
import re

csv_path = 'recipes_extended.csv'

# Read CSV and analyze
all_recipes = []
title_variants = defaultdict(list)
exact_dupes = defaultdict(int)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    print(f"Columns: {cols}\n")
    
    for idx, row in enumerate(reader):
        all_recipes.append(row)
        title = (row.get('recipe_title') or '').strip()
        
        # Track exact duplicates
        key = (title, row.get('ingredients_raw', ''), row.get('directions_raw', ''))
        exact_dupes[key[:1]] += 1
        
        # Track title variants (remove modifiers)
        base_title = re.sub(r'\b(air fryer|instant pot|mini|beef|chicken|vegetarian|vegan|quick|easy|homemade)\b', '', title, flags=re.IGNORECASE).strip()
        title_variants[base_title].append(title)

print(f"Total recipes: {len(all_recipes)}")
print(f"Unique titles: {len(set(r.get('recipe_title', '') for r in all_recipes))}")

# Show examples of duplicates
dupes = [k for k, v in exact_dupes.items() if v > 1]
print(f"\nExact duplicate titles found: {len(dupes)}")
if dupes[:5]:
    print("Examples:")
    for title, count in list(exact_dupes.items())[:5]:
        if count > 1:
            print(f"  - '{title[0]}' appears {count} times")

# Show examples of variants
variants_with_multiple = {k: v for k, v in title_variants.items() if len(v) > 1}
print(f"\nRecipe variants (same base dish, different types): {len(variants_with_multiple)}")
if variants_with_multiple:
    for base, titles in list(variants_with_multiple.items())[:10]:
        if base and titles:
            print(f"  Base: '{base}'")
            for t in titles[:3]:
                print(f"    - {t}")
