SOURCE_WEIGHTS = {
    "script": 1.0,
    "slide": 0.6,
}

def intrinsic_weight(text: str) -> float:
    t = text.lower()

    if any(k in t for k in ["is", "means", "defined as"]):
        return 1.0
    if any(k in t for k in ["important", "key", "main idea"]):
        return 0.9
    if any(k in t for k in ["for example", "for instance"]):
        return 0.5
    if any(k in t for k in ["next", "moving on"]):
        return 0.3
    return 0.7
