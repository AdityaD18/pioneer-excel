import re

# WAGO-style part numbers in this catalog always start with a digit and are
# made of dash/slash-separated alphanumeric segments, e.g.:
#   206-118, 209-504, 2002-1201, 8002-100/1000-693, 0281-0904/0981-0000
# As soon as a token stops looking like that (a space followed by anything
# that isn't a continuing "-segment" or "/segment"), the rest of the cell is
# treated as free-text description.
_PART_NUMBER_RE = re.compile(r'^([0-9]+(?:[-/][0-9A-Za-z]+)*)\s*[-:]?\s*(.*)$')


def split_part_number_and_description(raw_cell):
    """
    Splits a single Excel cell that contains both the part number and a
    free-text description together, e.g.:
        "209-504 Push-in terminal block, 2-conductor"
        -> ("209-504", "Push-in terminal block, 2-conductor")

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
    description = match.group(2).strip()
    return part_no, description
