import re
from typing import Optional, Tuple

EpisodeInfo = Tuple[Optional[int], Optional[int]]

_WORD_TO_NUMBER = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "twentyone": 21,
    "twentytwo": 22,
    "twentythree": 23,
    "twentyfour": 24,
    "twentyfive": 25,
    "twentysix": 26,
    "twentyseven": 27,
    "twentyeight": 28,
    "twentynine": 29,
    "thirty": 30,
}

_ORDINAL_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
}


def _parse_numeric_token(value: str) -> Optional[int]:
    """Turn a numeric token or spelled-out number into an int."""
    if value is None:
        return None

    text = str(value).strip().lower()

    if not text:
        return None

    if text.isdigit():
        return int(text)

    if text in _WORD_TO_NUMBER:
        return _WORD_TO_NUMBER[text]

    if text in _ORDINAL_WORDS:
        return _ORDINAL_WORDS[text]

    return None


SEASON_EPISODE_PATTERNS = (
    # S01E08
    # S1E8
    # S01 E08
    # S01.E08
    # S01-E08
    re.compile(
        r"\bs(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)[\s._-]*e(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)\b",
        re.IGNORECASE,
    ),

    # Season 1 Episode 8
    # Season 1 Ep 8
    # Season 01 - Episode 08
    # Season two episode five
    re.compile(
        r"\bseason[\s._-]*(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)[\s._-]*(?:episode|ep)[\s._-]*(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)\b",
        re.IGNORECASE,
    ),

    # S1 Episode 8
    # S1 Ep 8
    re.compile(
        r"\bs(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)[\s._-]*(?:episode|ep)[\s._-]*(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)\b",
        re.IGNORECASE,
    ),

    # 1x08
    # 01x08
    # 1 x 08
    re.compile(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)\s*x\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twentyone|twentytwo|twentythree|twentyfour|twentyfive|twentysix|twentyseven|twentyeight|twentynine|thirty)\b",
        re.IGNORECASE,
    ),
)


# Patterns containing only an episode number.
#
# Group 1 = episode
EPISODE_ONLY_PATTERNS = (
    # 2nd Episode
    # 3rd Ep
    # 8th Episode
    re.compile(
        r"\b(\d+|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth)(?:st|nd|rd|th)[\s._-]*(?:episode|ep)\b",
        re.IGNORECASE,
    ),

    # Episode 2
    # Episode five
    # Ep 2
    re.compile(
        r"\b(?:episode|ep)[\s._-]*(\d+|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth)\b",
        re.IGNORECASE,
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_text(text: object) -> str:
    """
    Convert input into a searchable string.

    We intentionally keep common media filename separators here because
    patterns such as S01.E08 and S01-E08 should still be detectable.
    """

    if text is None:
        return ""

    return str(text).strip()


def _normalize_title(text: str) -> str:
    """
    Normalize a media title after episode information has been removed.

    Example:

        "The.Last.of.Us.S01E03.1080p"

    becomes approximately:

        "the last of us 1080p"

    Resolution/codec cleanup belongs in the general filename matching layer,
    not in this module.
    """

    text = re.sub(
        r"[^a-zA-Z0-9]+",
        " ",
        text,
    )

    return " ".join(text.lower().split())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_episode_info(text: object) -> EpisodeInfo:
    """
    Extract season and episode numbers from text.

    Returns:
        (season, episode)

    Examples:
        "S01E08"                   -> (1, 8)
        "S1 Ep 8"                  -> (1, 8)
        "Season 2 Episode 4"       -> (2, 4)
        "02x04"                    -> (2, 4)
        "Episode 7"                -> (None, 7)
        "7th Episode"              -> (None, 7)
        "Breaking Bad"             -> (None, None)
    """

    value = _clean_text(text)

    if not value:
        return None, None

    # First try formats containing both season and episode.
    for pattern in SEASON_EPISODE_PATTERNS:
        match = pattern.search(value)

        if match:
            season = _parse_numeric_token(match.group(1))
            episode = _parse_numeric_token(match.group(2))

            if season is not None and episode is not None:
                return season, episode

    # Then try episode-only formats.
    for pattern in EPISODE_ONLY_PATTERNS:
        match = pattern.search(value)

        if match:
            episode = _parse_numeric_token(match.group(1))

            if episode is not None:
                return None, episode

    return None, None


def remove_episode_info(text: object) -> str:
    """
    Remove recognized season/episode notation from text.

    This lets the matching system score the show title independently from
    the requested season and episode.

    Examples:
        "Lanterns S01E02"
            -> "lanterns"

        "Lanterns Season 1 Episode 2"
            -> "lanterns"

        "The.Last.of.Us.01x03"
            -> "the last of us"

        "Lanterns 2nd Episode"
            -> "lanterns"
    """

    value = _clean_text(text)

    if not value:
        return ""

    # Remove season + episode expressions.
    for pattern in SEASON_EPISODE_PATTERNS:
        value = pattern.sub(" ", value)

    # Remove episode-only expressions.
    for pattern in EPISODE_ONLY_PATTERNS:
        value = pattern.sub(" ", value)

    return _normalize_title(value)


def has_episode_info(text: object) -> bool:
    """
    Return True when text contains recognizable episode information.
    """

    season, episode = extract_episode_info(text)

    return season is not None or episode is not None


def format_episode_code(
    season: Optional[int],
    episode: Optional[int],
) -> Optional[str]:
    """
    Convert parsed episode information into standard SxxExx notation.

    Examples:
        (1, 2)    -> "S01E02"
        (12, 4)   -> "S12E04"
        (None, 2) -> "E02"
        (None, None) -> None
    """

    if episode is None:
        return None

    if season is None:
        return f"E{episode:02d}"

    return f"S{season:02d}E{episode:02d}"