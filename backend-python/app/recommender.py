from sentence_transformers import SentenceTransformer
import numpy as np
import json
import re
import os
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy import or_
from app.database import SessionLocal
from app.models import Recipe
from app.schemas import RecommendRequest, Recommendation
from app import crud

class RecipeRecommender:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Local model, no API
        self.max_candidates = 2000
        self.enable_innovation_scoring = os.getenv("ENABLE_INNOVATION_SCORING", "1") != "0"
        self.warmup_on_startup = self._env_bool("RECOMMENDER_WARMUP_ON_STARTUP", True)
        self.warmup_batch_size = self._env_int("RECOMMENDER_WARMUP_BATCH_SIZE", 256, min_value=16)
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.ingredient_pair_cache: Dict[str, List[Tuple[str, str]]] = {}
        self._embeddings_warmed = False

    def _env_bool(self, key: str, default: bool) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        value = raw.strip().lower()
        if value in {"1", "true", "yes", "y", "on"}:
            return True
        if value in {"0", "false", "no", "n", "off"}:
            return False
        return default

    def _env_int(self, key: str, default: int, min_value: int = 1) -> int:
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            parsed = int(raw)
        except Exception:
            return default
        return max(min_value, parsed)

    def _collapse_variant_candidates(self, recipes: List[Recipe]) -> List[Recipe]:
        """Keep one representative recipe per base recipe key, preferring standard variants."""
        grouped: Dict[str, Recipe] = {}

        for recipe in recipes:
            key = ((recipe.base_recipe or recipe.title or "").strip().lower())
            if not key:
                key = str(recipe.id)

            current = grouped.get(key)
            if current is None:
                grouped[key] = recipe
                continue

            current_is_standard = (current.variant_type or "").strip().lower() == "standard"
            recipe_is_standard = (recipe.variant_type or "").strip().lower() == "standard"

            if recipe_is_standard and not current_is_standard:
                grouped[key] = recipe

        return list(grouped.values())

    def _load_data(self):
        # Keep reload inexpensive for large datasets by clearing runtime caches.
        self.embedding_cache.clear()
        self.ingredient_pair_cache.clear()
        self._embeddings_warmed = False

    def warmup_embeddings(self, batch_size: Optional[int] = None) -> dict:
        effective_batch_size = batch_size if batch_size is not None else self.warmup_batch_size
        if self._embeddings_warmed and self.embedding_cache:
            return {
                "recipes_loaded": len(self.embedding_cache),
                "embedding_cache_entries": len(self.embedding_cache),
            }

        db = SessionLocal()
        try:
            recipes = db.query(Recipe.id, Recipe.main_ingredients, Recipe.title).order_by(Recipe.id.asc()).all()
        finally:
            db.close()

        texts: List[str] = []
        recipe_ids: List[str] = []
        for recipe_id, main_ingredients, title in recipes:
            if recipe_id in self.embedding_cache:
                continue

            main_ings = self._safe_parse_string_list(main_ingredients or '[]')
            text = ' '.join(main_ings) if len(main_ings) > 0 else (title or '')
            texts.append(text)
            recipe_ids.append(recipe_id)

            if len(texts) >= effective_batch_size:
                self._cache_embeddings(recipe_ids, texts)
                texts = []
                recipe_ids = []

        if texts:
            self._cache_embeddings(recipe_ids, texts)

        self._embeddings_warmed = True
        return {
            "recipes_loaded": len(recipes),
            "embedding_cache_entries": len(self.embedding_cache),
        }

    def _cache_embeddings(self, recipe_ids: List[str], texts: List[str]) -> None:
        if not texts:
            return

        encoded = self.model.encode(texts)
        norms = np.linalg.norm(encoded, axis=1, keepdims=True)
        norms[norms == 0] = 1
        encoded = (encoded / norms).astype(np.float32, copy=False)

        for idx, recipe_id in enumerate(recipe_ids):
            self.embedding_cache[recipe_id] = encoded[idx]

    def reload(self) -> dict:
        self._load_data()
        warmup_stats = self.warmup_embeddings(self.warmup_batch_size)

        return {
            **warmup_stats,
        }

    def recommend(self, request: RecommendRequest) -> List[Recommendation]:
        user_ingredients_raw = [i for i in (request.ingredients or []) if i and i.strip()]
        user_ingredients_norm = [self._normalize_ingredient(i) for i in user_ingredients_raw]
        user_ingredients_norm = [u for u in user_ingredients_norm if u]

        budget_limit = float(request.budget_limit) if request.budget_limit else None
        health_goal = (request.health_goal or "").strip().lower() or None
        waste_mode = bool(request.waste_mode)
        pantry_expiring = self._normalize_pantry_items(request.pantry_items if waste_mode else [])
        user_learning_profile: dict = {}

        db = SessionLocal()
        try:
            if request.user_id:
                user_learning_profile = crud.get_user_learning_profile(db, request.user_id)
            candidate_recipes = self._fetch_candidates(db, request, user_ingredients_norm)
        finally:
            db.close()

        if len(candidate_recipes) == 0:
            return []

        recommendations = self._score_candidate_recipes(
            candidate_recipes,
            user_ingredients_norm,
            pantry_expiring,
            budget_limit,
            health_goal,
            waste_mode,
            user_learning_profile,
            require_overlap=True,
            fallback_note=None,
        )

        if len(recommendations) == 0 and len(user_ingredients_norm) > 0:
            recommendations = self._score_candidate_recipes(
                candidate_recipes,
                user_ingredients_norm,
                pantry_expiring,
                budget_limit,
                health_goal,
                waste_mode,
                user_learning_profile,
                require_overlap=False,
                fallback_note="No direct ingredient matches found, so the search was broadened to suggest the closest recipes.",
            )

        return recommendations[:10]

    def _score_candidate_recipes(
        self,
        candidate_recipes: List[Recipe],
        user_ingredients_norm: List[str],
        pantry_expiring: List[Tuple[str, int]],
        budget_limit: Optional[float],
        health_goal: Optional[str],
        waste_mode: bool,
        user_learning_profile: dict,
        require_overlap: bool,
        fallback_note: Optional[str],
    ) -> List[Recommendation]:
        # Create query embedding from normalized user ingredients
        query_text = ' '.join(user_ingredients_norm)
        query_embedding = self.model.encode([query_text])
        query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        query_norm[query_norm == 0] = 1
        query_embedding = query_embedding / query_norm

        candidate_embeddings = self._get_embeddings_for_candidates(candidate_recipes)
        similarities = (candidate_embeddings @ query_embedding.T).flatten()

        recommendations: List[Recommendation] = []
        for idx, recipe in enumerate(candidate_recipes):

            recipe_ingredient_pairs = self._extract_recipe_ingredients(recipe)
            recipe_norm = [item[1] for item in recipe_ingredient_pairs]

            available_display, missing_display, overlap_count = self._match_ingredients(
                user_ingredients_norm,
                recipe_ingredient_pairs,
            )

            if require_overlap and len(user_ingredients_norm) > 0 and overlap_count == 0:
                continue

            overlap_ratio = overlap_count / max(1, len(user_ingredients_norm))
            coverage_ratio = overlap_count / max(1, len(recipe_norm))
            semantic_score = float(similarities[idx])

            # Innovation modes: zero-waste, budget and health fit.
            waste_score = self._compute_waste_score(recipe_ingredient_pairs, pantry_expiring) if waste_mode else 0.0
            budget_score = self._compute_budget_score(recipe, budget_limit) if budget_limit else 0.0
            health_score = self._compute_health_score(recipe, health_goal) if health_goal else 0.0
            learning_score, learning_notes = self._compute_learning_score(recipe, user_learning_profile)

            # Overlap-first scoring. Semantic similarity only nudges ordering.
            final_score = (overlap_ratio * 70.0) + (coverage_ratio * 20.0) + (semantic_score * 10.0)
            if self.enable_innovation_scoring:
                final_score += (waste_score * 18.0) + (budget_score * 10.0) + (health_score * 12.0) + (learning_score * 14.0)

            reason = f"Matches {overlap_count} of your ingredients"
            explanation = [
                f"Ingredient overlap: {overlap_count}/{max(1, len(user_ingredients_norm))}",
                f"Coverage score: {coverage_ratio * 100:.0f}%",
                f"Semantic similarity: {max(0.0, semantic_score) * 100:.0f}%",
            ]
            if fallback_note:
                explanation.insert(0, fallback_note)
            if waste_mode and pantry_expiring:
                urgency_text = self._pantry_urgency_summary(pantry_expiring, recipe_ingredient_pairs)
                explanation.append(f"Zero-waste boost: {waste_score * 100:.0f}% ({urgency_text})")
            if budget_limit:
                estimated_cost = self._estimate_recipe_cost(recipe)
                explanation.append(f"Budget fit: est. ${estimated_cost:.2f} vs ${budget_limit:.2f}")
            if health_goal:
                explanation.append(f"Health goal ({health_goal}) fit: {health_score * 100:.0f}%")
            if learning_notes:
                explanation.extend(learning_notes)

            recommendations.append(Recommendation(
                id=recipe.id,
                score=max(0.0, min(100.0, final_score)),
                reason=reason if not fallback_note else f"{reason} - broadened search",
                explanation=explanation,
                modifications=explanation,
                missing_ingredients=missing_display,
                available_ingredients=available_display,
                recipe=recipe,
            ))

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations

    def _compute_learning_score(self, recipe: Recipe, learning_profile: dict) -> Tuple[float, List[str]]:
        if not learning_profile:
            return 0.0, []

        notes: List[str] = []
        cuisine = (recipe.cuisine or "").strip().lower()
        tags = []
        try:
            parsed_tags = json.loads(recipe.tags or "[]")
            if isinstance(parsed_tags, list):
                tags = [str(tag).strip().lower() for tag in parsed_tags if str(tag).strip()]
        except Exception:
            tags = []

        accepted_cuisines = learning_profile.get("accepted_cuisines", {}) if isinstance(learning_profile.get("accepted_cuisines", {}), dict) else {}
        rejected_cuisines = learning_profile.get("rejected_cuisines", {}) if isinstance(learning_profile.get("rejected_cuisines", {}), dict) else {}
        accepted_tags = learning_profile.get("accepted_tags", {}) if isinstance(learning_profile.get("accepted_tags", {}), dict) else {}
        rejected_tags = learning_profile.get("rejected_tags", {}) if isinstance(learning_profile.get("rejected_tags", {}), dict) else {}

        accepted_total = int(learning_profile.get("accepted_count", 0) or 0)
        rejected_total = int(learning_profile.get("rejected_count", 0) or 0)
        total = accepted_total + rejected_total
        if total == 0:
            return 0.0, []

        scale = min(1.0, total / 8.0)
        bonus = 0.0

        if cuisine and cuisine in accepted_cuisines:
            bonus += 0.35 + min(0.25, accepted_cuisines.get(cuisine, 0) / 10.0)
            notes.append(f"Learns your preference for {cuisine}")
        if cuisine and cuisine in rejected_cuisines:
            bonus -= 0.35 + min(0.2, rejected_cuisines.get(cuisine, 0) / 12.0)
            notes.append(f"Downweighted because you rejected {cuisine} before")

        tag_hits = 0
        for tag in tags:
            if tag in accepted_tags:
                tag_hits += 1
            if tag in rejected_tags:
                tag_hits -= 1

        if tag_hits > 0:
            bonus += min(0.35, 0.08 * tag_hits)
            notes.append("Matches your past positive feedback")
        elif tag_hits < 0:
            bonus -= min(0.3, 0.08 * abs(tag_hits))
            notes.append("Lowered from past negative feedback")

        return max(-1.0, min(1.0, bonus * scale)), notes

    def _pantry_urgency_summary(self, pantry_expiring: List[Tuple[str, int]], recipe_ingredient_pairs: List[Tuple[str, str]]) -> str:
        if not pantry_expiring:
            return ""
        recipe_norms = [norm for _, norm in recipe_ingredient_pairs]
        matched_items = []
        for pantry_norm, days in pantry_expiring:
            if any(self._is_match(pantry_norm, recipe_norm) for recipe_norm in recipe_norms):
                matched_items.append(f"{pantry_norm} in {days}d")
        if not matched_items:
            return "No urgent pantry overlap"
        return "Uses " + ", ".join(matched_items[:3])

    def _normalize_pantry_items(self, pantry_items: Optional[List[Any]]) -> List[Tuple[str, int]]:
        normalized: List[Tuple[str, int]] = []
        seen = set()
        for item in (pantry_items or [])[:100]:
            name = ""
            days = 0
            if hasattr(item, "name"):
                name = str(getattr(item, "name", ""))
                days = int(getattr(item, "expires_in_days", 0) or 0)
            elif isinstance(item, dict):
                name = str(item.get("name", ""))
                days = int(item.get("expires_in_days", 0) or 0)

            norm = self._normalize_ingredient(name)
            if not norm or norm in seen:
                continue
            seen.add(norm)
            normalized.append((norm, max(0, min(30, days))))
        return normalized

    def _compute_waste_score(
        self,
        recipe_ingredient_pairs: List[Tuple[str, str]],
        pantry_expiring: List[Tuple[str, int]],
    ) -> float:
        if not pantry_expiring:
            return 0.0

        recipe_norms = [norm for _, norm in recipe_ingredient_pairs]
        weighted_hits = 0.0
        weighted_total = 0.0
        for pantry_norm, days in pantry_expiring:
            urgency_weight = 1.0 + max(0, (10 - days)) / 6.0
            weighted_total += urgency_weight
            if any(self._is_match(pantry_norm, recipe_norm) for recipe_norm in recipe_norms):
                weighted_hits += urgency_weight

        if weighted_total == 0:
            return 0.0
        return min(1.0, weighted_hits / weighted_total)

    def _estimate_recipe_cost(self, recipe: Recipe) -> float:
        ingredients = self._extract_recipe_ingredients(recipe)
        ingredient_count = max(1, len(ingredients))
        # Simple heuristic for demo-friendly budget fit.
        return round((ingredient_count * 0.75) + 1.5, 2)

    def _compute_budget_score(self, recipe: Recipe, budget_limit: Optional[float]) -> float:
        if not budget_limit or budget_limit <= 0:
            return 0.0
        est_cost = self._estimate_recipe_cost(recipe)
        if est_cost <= budget_limit:
            return min(1.0, 0.6 + ((budget_limit - est_cost) / max(1.0, budget_limit)))
        overshoot = (est_cost - budget_limit) / max(1.0, budget_limit)
        return max(0.0, 0.6 - overshoot)

    def _extract_nutrition(self, recipe: Recipe) -> Dict[str, Any]:
        try:
            parsed = json.loads(recipe.nutrition or "{}")
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {}

    def _compute_health_score(self, recipe: Recipe, health_goal: Optional[str]) -> float:
        if not health_goal:
            return 0.0

        goal = health_goal.lower()
        nutrition = self._extract_nutrition(recipe)
        tags = [t.lower() for t in self._safe_parse_string_list(recipe.tags or "[]")]
        ingredients_norm = [norm for _, norm in self._extract_recipe_ingredients(recipe)]

        if goal in {"high-protein", "high_protein"}:
            protein = float(nutrition.get("protein", 0) or 0)
            protein_hits = {"egg", "chicken", "fish", "lentil", "dal", "paneer", "tofu"}
            token_hit = 1.0 if any(tok in ingredients_norm for tok in protein_hits) else 0.0
            numeric = min(1.0, protein / 25.0)
            return max(token_hit, numeric)

        if goal in {"low-calorie", "low_calorie"}:
            calories = float(nutrition.get("calories", 0) or 0)
            if calories > 0:
                return max(0.0, min(1.0, (500.0 - calories) / 300.0))
            healthiness = float(nutrition.get("healthiness_score", 0) or 0)
            return max(0.0, min(1.0, healthiness / 100.0))

        if goal == "balanced":
            healthiness = float(nutrition.get("healthiness_score", 0) or 0)
            base = max(0.0, min(1.0, healthiness / 100.0))
            if "vegetarian" in tags or "vegan" in tags:
                base = min(1.0, base + 0.1)
            return base

        return 0.0

    def _fetch_candidates(self, db, request: RecommendRequest, user_ingredients_norm: List[str]) -> List[Recipe]:
        query = db.query(Recipe)

        if request.time_limit:
            query = query.filter(Recipe.total_time <= request.time_limit)

        if request.cuisine:
            query = query.filter(Recipe.cuisine.ilike(f"%{request.cuisine.strip()}%"))

        if request.diet:
            if request.diet == "veg":
                query = query.filter(Recipe.tags.ilike('%"veg"%'))
            elif request.diet == "non-veg":
                query = query.filter(Recipe.tags.ilike('%"non-veg"%'))
            else:
                query = query.filter(Recipe.tags.ilike(f"%{request.diet.strip().lower()}%"))

        ingredient_terms = []
        for ingredient in user_ingredients_norm:
            for token in ingredient.split():
                if len(token) > 2:
                    ingredient_terms.append(token)

        ingredient_terms = list(dict.fromkeys(ingredient_terms))[:8]
        if ingredient_terms:
            main_ingredient_filters = [Recipe.main_ingredients.ilike(f"%{term}%") for term in ingredient_terms]
            query = query.filter(or_(*main_ingredient_filters))

        candidates = query.limit(self.max_candidates * 3).all()
        candidates = self._collapse_variant_candidates(candidates)
        candidates = candidates[: self.max_candidates]

        if len(candidates) == 0:
            fallback_query = db.query(Recipe)
            if request.time_limit:
                fallback_query = fallback_query.filter(Recipe.total_time <= request.time_limit)
            if request.cuisine:
                fallback_query = fallback_query.filter(Recipe.cuisine.ilike(f"%{request.cuisine.strip()}%"))
            if request.diet:
                if request.diet == "veg":
                    fallback_query = fallback_query.filter(Recipe.tags.ilike('%"veg"%'))
                elif request.diet == "non-veg":
                    fallback_query = fallback_query.filter(Recipe.tags.ilike('%"non-veg"%'))
                else:
                    fallback_query = fallback_query.filter(Recipe.tags.ilike(f"%{request.diet.strip().lower()}%"))
            candidates = fallback_query.limit(self.max_candidates * 3).all()
            candidates = self._collapse_variant_candidates(candidates)
            candidates = candidates[: self.max_candidates]

        return candidates

    def _get_embeddings_for_candidates(self, recipes: List[Recipe]) -> np.ndarray:
        missing_indices: List[int] = []
        missing_texts: List[str] = []

        for idx, recipe in enumerate(recipes):
            if recipe.id not in self.embedding_cache:
                main_ings = self._safe_parse_string_list(recipe.main_ingredients or '[]')
                text = ' '.join(main_ings) if len(main_ings) > 0 else (recipe.title or '')
                missing_indices.append(idx)
                missing_texts.append(text)

        if missing_texts:
            self._cache_embeddings([recipes[recipe_idx].id for recipe_idx in missing_indices], missing_texts)

        return np.stack([self.embedding_cache[r.id] for r in recipes], axis=0)

    def _safe_parse_string_list(self, value: str) -> List[str]:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v) for v in parsed if str(v).strip()]
        except Exception:
            pass
        return [x.strip() for x in value.split(',') if x.strip()]

    def _extract_recipe_ingredients(self, recipe: Any) -> List[Tuple[str, str]]:
        cached = self.ingredient_pair_cache.get(recipe.id)
        if cached is not None:
            return cached

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

        self.ingredient_pair_cache[recipe.id] = dedup
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

        # Token-based overlap, with guards for derivative ingredients
        # like "rice flour" or "rice vinegar" when user asked for "rice".
        a_tokens = self._normalized_token_set(a)
        b_tokens = self._normalized_token_set(b)

        if self._is_base_to_derivative_mismatch(a_tokens, b_tokens):
            return False
        if self._is_base_to_derivative_mismatch(b_tokens, a_tokens):
            return False

        return len(a_tokens.intersection(b_tokens)) > 0

    def _is_base_to_derivative_mismatch(self, base_tokens: set, candidate_tokens: set) -> bool:
        if len(base_tokens) != 1 or len(candidate_tokens) <= 1:
            return False

        base = next(iter(base_tokens))
        if base not in candidate_tokens:
            return False

        derivative_blockers = {
            "rice": {
                "flour",
                "vinegar",
                "powder",
                "starch",
                "bran",
                "milk",
                "water",
                "wine",
                "syrup",
                "oil",
            },
        }

        blocked_terms = derivative_blockers.get(base, set())
        return len(candidate_tokens.intersection(blocked_terms)) > 0

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