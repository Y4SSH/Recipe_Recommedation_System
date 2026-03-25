import csv
import json
import uuid
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Recipe
from app.food_classifier import classify_veg_nonveg

# Create tables
Base.metadata.create_all(bind=engine)

def import_csv(csv_path: str):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        db = SessionLocal()
        try:
            count = 0
            for row in reader:
                # Parse ingredients
                ing_text = row['TranslatedIngredients']
                ingredients = []
                for ing in ing_text.split(','):
                    ing = ing.strip()
                    if ing:
                        parts = ing.split()
                        if len(parts) >= 1:
                            qty = parts[0] if len(parts) > 0 else '1'
                            unit = parts[1] if len(parts) > 1 else 'unit'
                            name = ' '.join(parts[2:]) if len(parts) > 2 else ' '.join(parts)
                            ingredients.append({"name": name.lower(), "qty": qty, "unit": unit})
                
                # Parse steps
                steps = [step.strip() for step in row['TranslatedInstructions'].split('.') if step.strip()]
                
                # Main ingredients
                main_ings = [ing.strip().lower() for ing in row['Cleaned-Ingredients'].split(',') if ing.strip()]
                category = classify_veg_nonveg(main_ings)
                
                recipe = Recipe(
                    id=str(uuid.uuid4()),
                    title=row['TranslatedRecipeName'],
                    description=f"A delicious {row['Cuisine']} recipe",
                    ingredients=json.dumps(ingredients),
                    steps=json.dumps(steps),
                    cuisine=row['Cuisine'],
                    tags=json.dumps(['indian', category]),
                    cook_time=int(float(row['TotalTimeInMins']) * 0.7),
                    prep_time=int(float(row['TotalTimeInMins']) * 0.3),
                    total_time=int(float(row['TotalTimeInMins'])),
                    servings=4,
                    difficulty='medium',
                    nutrition=json.dumps({"calories": 400, "protein": 15, "carbs": 50, "fat": 10}),
                    image_url=row['image-url'] if row['image-url'] else None,
                    source_url=row['URL'] if row['URL'] else None,
                    main_ingredients=json.dumps(main_ings)
                )
                
                db.add(recipe)
                count += 1
                if count % 100 == 0:
                    print(f"Added {count} recipes...")
            
            db.commit()
            print(f"Import completed! Added {count} recipes.")
        
        except Exception as e:
            db.rollback()
            print(f"Error: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    import_csv("data/Cleaned_Indian_Food_Dataset.csv")