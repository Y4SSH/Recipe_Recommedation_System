import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional


DEAD_IMAGE_HOST_HINTS = (
    "archanaskitchen",
)


def _normalize_text(value: str) -> str:
    value = (value or "").lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _token_set(value: str) -> set:
    return {tok for tok in _normalize_text(value).split(" ") if tok}


def is_likely_dead_image_url(url: Optional[str]) -> bool:
    if not url:
        return True

    lowered = url.lower()
    return any(hint in lowered for hint in DEAD_IMAGE_HOST_HINTS)


@lru_cache(maxsize=1)
def _image_filename_index() -> Dict[str, str]:
    root_dir = Path(__file__).resolve().parents[2]
    images_dir = root_dir / "images" / "recipes"
    index: Dict[str, str] = {}

    if not images_dir.exists():
        return index

    for file in images_dir.iterdir():
        if not file.is_file():
            continue
        if file.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            continue
        index[_normalize_text(file.stem)] = file.name

    return index


@lru_cache(maxsize=1)
def _image_token_index() -> list:
    """Precompute token sets once to avoid repeated tokenization per request."""
    token_index = []
    for normalized_name, filename in _image_filename_index().items():
        name_tokens = _token_set(normalized_name)
        if not name_tokens:
            continue
        token_index.append((filename, name_tokens))
    return token_index


def _best_local_image_filename(recipe_title: str) -> Optional[str]:
    normalized_title = _normalize_text(recipe_title)
    if not normalized_title:
        return None

    # Fast path: exact normalized match.
    exact = _image_filename_index().get(normalized_title)
    if exact:
        return exact

    title_tokens = _token_set(normalized_title)
    if not title_tokens:
        return None

    best_name = None
    best_score = 0

    for filename, name_tokens in _image_token_index():
        overlap = len(title_tokens.intersection(name_tokens))
        if overlap > best_score:
            best_score = overlap
            best_name = filename

    if best_score == 0:
        return None

    return best_name


def resolve_recipe_image_url(recipe_title: str, image_url: Optional[str]) -> Optional[str]:
    if image_url and not is_likely_dead_image_url(image_url):
        return image_url

    local_filename = _best_local_image_filename(recipe_title)
    if local_filename:
        return f"/static/recipes/{local_filename}"

    return image_url
