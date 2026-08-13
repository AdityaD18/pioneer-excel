_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"
]
_TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
]


def _two_digits(n):
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return (_TENS[tens] + (" " + _ONES[ones] if ones else "")).strip()


def _three_digits(n):
    hundreds, rest = divmod(n, 100)
    parts = []
    if hundreds:
        parts.append(f"{_ONES[hundreds]} Hundred")
    if rest:
        parts.append(_two_digits(rest))
    return " ".join(parts)


def _integer_to_words(n):
    """Converts a non-negative integer to words using the Indian numbering
    system (Thousand / Lakh / Crore), e.g. 1234567 -> 'Twelve Lakh Thirty
    Four Thousand Five Hundred Sixty Seven'."""
    if n == 0:
        return "Zero"

    crore, n = divmod(n, 10000000)
    lakh, n = divmod(n, 100000)
    thousand, n = divmod(n, 1000)
    hundred = n

    parts = []
    if crore:
        parts.append(f"{_integer_to_words(crore)} Crore")
    if lakh:
        parts.append(f"{_two_digits(lakh) if lakh < 100 else _integer_to_words(lakh)} Lakh")
    if thousand:
        parts.append(f"{_two_digits(thousand) if thousand < 100 else _integer_to_words(thousand)} Thousand")
    if hundred:
        parts.append(_three_digits(hundred))

    return " ".join(parts)


def amount_to_words(amount, currency="Rupees", subunit="Paise"):
    """
    Converts a monetary amount (float) into words for the "Amount in Words"
    line expected on a professional Indian tax invoice, e.g.:
        amount_to_words(80715.92) -> "Rupees Eighty Thousand Seven Hundred
        Fifteen and Ninety Two Paise Only"
    """
    amount = round(float(amount or 0), 2)
    rupees = int(amount)
    paise = round((amount - rupees) * 100)

    words = f"{currency} {_integer_to_words(rupees)}"
    if paise:
        words += f" and {_two_digits(paise)} {subunit}"
    words += " Only"
    return words
