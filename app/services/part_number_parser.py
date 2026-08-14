import re

# WAGO-style part numbers in this catalog always start with a digit and are
# made of dash/slash-separated alphanumeric segments, e.g.:
#   206-118, 209-504, 2002-1201, 8002-100/1000-693, 0281-0904/0981-0000
# As soon as a token stops looking like that (a space followed by anything
# that isn't a continuing "-segment" or "/segment"), the rest of the cell is
# treated as free-text description.
_PART_NUMBER_RE = re.compile(r'^([0-9]+(?:[-/][0-9A-Za-z]+)*)\s*[-:]?\s*(.*)$')

# Real-world sheets from this customer wrap the description in one or two
# layers of parentheses together with a Minimum Order Quantity tag, in
# several inconsistent forms, e.g.:
#   "((MOQ-500) END CLAMP GREY)"
#   "((MOQ -200)2-conductor through terminal block; 4 mm²)"
#   "(MOQ (100) 2-conductor through terminal block; 1 mm²;)"
#   "(MOQ(100)2-conductor through terminal block; 1 mm²)"
#   "((MOQ-200))"                      <- MOQ only, no description text
_MOQ_RE = re.compile(r'MOQ\s*[-(]?\s*(\d+)', re.IGNORECASE)


def _clean_moq_wrapped_text(remainder):
    """Pulls the MOQ number out of a parenthesised '(MOQ-###) description'
    style fragment and returns clean 'description (MOQ ###)' text - parens
    are structural noise here, not meaningful content, so they're stripped
    rather than preserved."""
    moq_match = _MOQ_RE.search(remainder)
    moq_num = moq_match.group(1) if moq_match else None
    text = remainder[:moq_match.start()] + remainder[moq_match.end():] if moq_match else remainder

    text = text.replace('(', ' ').replace(')', ' ')
    text = re.sub(r'^[\s\-;:]+', '', text)
    text = re.sub(r'[\s\-;:]+$', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()

    if text and moq_num:
        return f"{text} (MOQ {moq_num})"
    if moq_num:
        return f"MOQ {moq_num}"
    return text


def split_part_number_and_description(raw_cell):
    """
    Splits a single Excel cell that contains both the part number and a
    free-text description together, e.g.:
        "209-504 Push-in terminal block, 2-conductor"
        -> ("209-504", "Push-in terminal block, 2-conductor")

    Also handles this customer's MOQ-wrapped format:
        "0249-0116/0981-0008 ((MOQ-500) END CLAMP GREY)"
        -> ("0249-0116/0981-0008", "END CLAMP GREY (MOQ 500)")

    If the cell is just a plain part number with nothing else, or doesn't
    match the expected pattern at all, the description comes back empty and
    the whole trimmed cell is returned as the part number - callers should
    treat an empty description as "nothing to split, use as-is".
    """
    raw = str(raw_cell or "").strip()
    if not raw or raw.lower() == "nan":
        return "", ""

    match = _PART_NUMBER_RE.match(raw)
    if not match:
        return raw, ""

    part_no = match.group(1).strip()
    remainder = match.group(2).strip()
    if not remainder:
        return part_no, ""

    description = _clean_moq_wrapped_text(remainder)
    return part_no, description
