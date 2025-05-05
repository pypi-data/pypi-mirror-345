import re

NAN_STRING = ""
NO_UNIT_STRING = "No Unit"
UNIT_PREFIX = " \n/ "
UNIT_SUFFIX = ""
SELECT_MEASURE = "Select Measure"
SELECT_UNIT = "Select Unit"


def title_case_latin(word: str) -> str:
    """Apply .title() only to ASCII words (fully Latin)."""
    return re.sub(r"[A-Za-z]+", lambda m: m.group(0).title(), word)


def pretty_title(title: str) -> str:
    """Title-case only Latin words and replace underscores with spaces."""
    words = title.replace("_", " ").split()
    return " ".join(title_case_latin(word) for word in words)
