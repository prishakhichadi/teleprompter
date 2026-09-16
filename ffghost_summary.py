def build_ghost_summary(summary_data, weight_threshold=0.6):
    strong = []
    missed = []

    for item in summary_data:
        if item["weight"] < weight_threshold:
            continue  # ignore low-importance content

        if item["matched"]:
            strong.append(item)
        else:
            missed.append(item)

    suggestions = build_suggestion(missed)

    return {
        "strong": strong,
        "missed": missed,
        "suggestions": suggestions
    }


def format_ghost_summary(summary):
    lines = []
    lines.append("GHOST SUMMARY\n")

    if summary["strong"]:
        lines.append("Strong coverage")
        for s in summary["strong"][:5]:
            lines.append(f"• {s['text']} (slide {s['slide'] + 1})")
        lines.append("")

    if summary["missed"]:
        lines.append("Missed / weak areas")
        for m in summary["missed"][:5]:
            lines.append(f"• {m['text']} (slide {m['slide'] + 1})")
        lines.append("")

    if summary["missed"]:
        lines.append("Suggestions")
        lines.append("• Consider adding brief explanations for the missed points above")

    return "\n".join(lines)


def build_suggestion(missed_items):
    if not missed_items:
        return []

    # pick most important missed item
    top = max(missed_items, key=lambda x: x["weight"])
    text = top["text"].lower()

    if any(k in text for k in [" is ", " means ", " defined as "]):
        tip = "Add a one-line definition early to anchor the concept."
    elif any(k in text for k in ["for example", "for instance"]):
        tip = "Include a concrete example to reinforce understanding."
    elif any(k in text for k in ["next", "moving on", "we will"]):
        tip = "Add a brief transition to clearly signal topic change."
    else:
        tip = "Briefly emphasize this idea to improve clarity."

    return [{
        "text": f"{tip} (Missed: {top['text']})"
    }]
