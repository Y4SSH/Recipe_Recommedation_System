from typing import Iterable

NON_VEG_KEYWORDS = {
    "chicken",
    "mutton",
    "lamb",
    "beef",
    "pork",
    "ham",
    "bacon",
    "sausage",
    "fish",
    "prawn",
    "shrimp",
    "crab",
    "lobster",
    "squid",
    "octopus",
    "egg",
    "eggs",
    "anchovy",
    "tuna",
    "salmon",
    "rohu",
    "katla",
    "keema",
}


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def classify_veg_nonveg(ingredients: Iterable[str]) -> str:
    for raw in ingredients:
        ing = normalize_text(raw)
        # Token-level checks reduce false positives from arbitrary substrings.
        tokens = set(ing.replace("-", " ").replace("/", " ").split())
        if any(k in tokens for k in NON_VEG_KEYWORDS):
            return "non-veg"
        if "egg" in ing and "eggplant" not in ing:
            return "non-veg"
    return "veg"
