from sentence_transformers import SentenceTransformer
import numpy as np
import json
import re
from typing import List, Dict, Any, Tuple
from app.crud import get_all_recipes
from app.database import SessionLocal
from app.schemas import RecommendRequest, Recommendation

class RecipeRecommender:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Local model, no API
        self.recipes = []
        self.embeddings = None
        self._load_data()

    def _load_data(self):
        self.recipes = []
        self.embeddings = None
        # Load recipes from database
        db = SessionLocal()
        try:
            recipes = get_all_recipes(db)
            self.recipes = recipes
            # Create embeddings for main ingredients
            texts = []
            for recipe in recipes:
                main_ings = json.loads(recipe.main_ingredients or '[]')
                text = ' '.join(main_ings)
                texts.append(text)

            if texts:
                self.embeddings = self.model.encode(texts)
                # Normalize embeddings for cosine similarity
                norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
                norms[norms == 0] = 1
                self.embeddings = self.embeddings / norms
        finally:
            db.close()

    def reload(self) -> dict:
        self._load_data()
        return {
            "recipes_loaded": len(self.recipes),
            "embeddings_ready": self.embeddings is not None,
        }

    def recommend(self, request: RecommendRequest) -> List[Recommendation]:
        if self.embeddings is None or len(self.recipes) == 0:
            return []

        user_ingredients_raw = [i for i in (request.ingredients or []) if i and i.strip()]
        user_ingredients_norm = [self._normalize_ingredient(i) for i in user_ingredients_raw]

        # Create query embedding from normalized user ingredients
        query_text = ' '.join(user_ingredients_norm)
        query_embedding = self.model.encode([query_text])
        query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        query_norm[query_norm == 0] = 1
        query_embedding = query_embedding / query_norm

        # Cosine similarity with all recipe embeddings
        similarities = (self.embeddings @ query_embedding.T).flatten()

        recommendations = []
        for idx, recipe in enumerate(self.recipes):
            if request.time_limit and recipe.total_time and recipe.total_time > request.time_limit:
                continue

            if request.cuisine and recipe.cuisine:
                if request.cuisine.lower() not in recipe.cuisine.lower():
                    continue

            if request.diet and recipe.tags:
                tags = self._safe_parse_string_list(recipe.tags)
                if request.diet.lower() not in [t.lower() for t in tags]:
                    continue

            recipe_ingredient_pairs = self._extract_recipe_ingredients(recipe)
            recipe_norm = [item[1] for item in recipe_ingredient_pairs]

            available_display, missing_display, overlap_count = self._match_ingredients(
                user_ingredients_norm,
                recipe_ingredient_pairs,
            )

            if len(user_ingredients_norm) > 0 and overlap_count == 0:
                continue

            overlap_ratio = overlap_count / max(1, len(user_ingredients_norm))
            coverage_ratio = overlap_count / max(1, len(recipe_norm))
            semantic_score = float(similarities[idx])

            # Overlap-first scoring. Semantic similarity only nudges ordering.
            final_score = (overlap_ratio * 70.0) + (coverage_ratio * 20.0) + (semantic_score * 10.0)

            reason = f"Matches {overlap_count} of your ingredients"

            recommendations.append(Recommendation(
                id=recipe.id,
                score=max(0.0, min(100.0, final_score)),
                reason=reason,
                missing_ingredients=missing_display,
                available_ingredients=available_display,
                recipe=recipe,
            ))

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:10]

    def _safe_parse_string_list(self, value: str) -> List[str]:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v) for v in parsed if str(v).strip()]
        except Exception:
            pass
        return [x.strip() for x in value.split(',') if x.strip()]

    def _extract_recipe_ingredients(self, recipe: Any) -> List[Tuple[str, str]]:
        # Returns list of tuples: (display_name, normalized_name)
        ingredients: List[str] = []

        if getattr(recipe, 'main_ingredients', None):
            ingredients.extend(self._safe_parse_string_list(recipe.main_ingredients))

        if getattr(recipe, 'ingredients', None):
            try:
                parsed = json.loads(recipe.ingredients)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and 'name' in item:
                            ingredients.append(str(item['name']))
                        elif isinstance(item, str):
                            ingredients.append(item)
            except Exception:
                ingredients.extend([x.strip() for x in str(recipe.ingredients).split(',') if x.strip()])

        dedup: List[Tuple[str, str]] = []
        seen = set()
        for ing in ingredients:
            norm = self._normalize_ingredient(ing)
            if not norm or norm in seen:
                continue
            seen.add(norm)
            dedup.append((ing.strip(), norm))

        return dedup

    def _match_ingredients(
        self,
        user_ings_norm: List[str],
        recipe_ingredient_pairs: List[Tuple[str, str]],
    ) -> Tuple[List[str], List[str], int]:
        available_display: List[str] = []
        missing_display: List[str] = []

        for display, recipe_norm in recipe_ingredient_pairs:
            matched = any(self._is_match(u, recipe_norm) for u in user_ings_norm)
            if matched:
                available_display.append(display)
            else:
                missing_display.append(display)

        overlap_count = 0
        for user_ing in user_ings_norm:
            if any(self._is_match(user_ing, r_norm) for _, r_norm in recipe_ingredient_pairs):
                overlap_count += 1

        return available_display, missing_display, overlap_count

    def _is_match(self, a: str, b: str) -> bool:
        if not a or not b:
            return False
        if a == b:
            return True

        # Token-based overlap prevents false positives like "egg" -> "eggplant"
        a_tokens = self._normalized_token_set(a)
        b_tokens = self._normalized_token_set(b)
        return len(a_tokens.intersection(b_tokens)) > 0

    def _normalized_token_set(self, text: str) -> set:
        tokens = [t.strip() for t in text.split() if t.strip()]
        normalized = set()

        for t in tokens:
            normalized.add(t)
            # Basic singularization for common plural forms
            if len(t) > 3 and t.endswith('es'):
                normalized.add(t[:-2])
            elif len(t) > 2 and t.endswith('s'):
                normalized.add(t[:-1])

        return normalized

    def _normalize_ingredient(self, value: str) -> str:
        text = (value or '').lower()
        text = re.sub(r'\([^)]*\)', ' ', text)
        text = re.sub(r'[^a-z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # common singular/plural and spelling normalization
        replacements = {
            'eggs': 'egg',
            'tomatoes': 'tomato',
            'potatoes': 'potato',
            'onions': 'onion',
            'chilies': 'chilli',
            'chillies': 'chilli',
            'cloves garlic': 'garlic',
            'garlic cloves': 'garlic',
            'spring onion greens': 'spring onion',
        }

        return replacements.get(text, text)

# Global instance
recommender = RecipeRecommender()