import difflib
import re

from .episodes import (
    extract_episode_info,
    remove_episode_info,
)


_UNWANTED_TITLE_MARKERS = {
    "trailer",
    "teaser",
    "preview",
    "sample",
    "clip",
    "thumbnail",
    "subtitle",
    "subtitles",
    "captions",
}

_VIDEO_METADATA_TOKENS = {
    "1080p",
    "720p",
    "2160p",
    "480p",
    "4k",
    "x264",
    "x265",
    "h264",
    "hevc",
    "hdrip",
    "bdrip",
    "webdl",
    "webrip",
    "web dl",
    "web rip",
    "remux",
    "bluray",
    "hdtv",
}

_GENERIC_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "dl",
    "episode",
    "ep",
    "file",
    "find",
    "for",
    "from",
    "image",
    "in",
    "launch",
    "locate",
    "movie",
    "music",
    "my",
    "of",
    "on",
    "open",
    "play",
    "please",
    "season",
    "series",
    "show",
    "start",
    "the",
    "to",
    "video",
    "watch",
    "web",
    "with",
    "rip",
}

_SUBTITLE_EXTENSIONS = {
    ".srt",
    ".sub",
    ".ass",
    ".ssa",
    ".vtt",
}


def _normalize_text(text):
    """
    Normalize text for comparison.

    Converts to lowercase, replaces non-alphanumeric characters
    with spaces, and collapses repeated whitespace.
    """

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return " ".join(text.split())


def _get_keywords(text):
    """
    Extract meaningful keywords from normalized text.

    This intentionally drops command words and release metadata so the
    actual title dominates the search score.
    """

    normalized = _normalize_text(text)
    if not normalized:
        return []

    keywords = []

    for word in normalized.split():
        if len(word) < 2:
            continue

        if word in _GENERIC_STOPWORDS:
            continue

        if word in _VIDEO_METADATA_TOKENS:
            continue

        keyword_variants = {word, word.replace("-", "")}
        if keyword_variants & _VIDEO_METADATA_TOKENS:
            continue

        keywords.append(word)

    return keywords


def _count_extra_keywords(query_keywords, filename_keywords):
    """Return how many filename keywords are not part of the request."""

    query_set = set(query_keywords)
    filename_set = set(filename_keywords)

    return len(filename_set - query_set)


def _count_unwanted_markers(filename_text):
    """Count filename markers that usually indicate a non-primary file."""

    normalized = _normalize_text(filename_text)

    if not normalized:
        return 0

    count = 0

    for marker in _UNWANTED_TITLE_MARKERS:
        if marker in normalized:
            count += 1

    for marker in _VIDEO_METADATA_TOKENS:
        if marker in normalized:
            count += 1

    return count


def score_title(query, filename_stem):
    """
    Calculate how closely a filename matches the search query.

    Uses:
    - Exact title matching
    - Full query matching
    - Word matching
    - Partial word matching
    - Fuzzy word matching
    - Overall fuzzy matching
    """

    query_normalized = _normalize_text(query)
    filename_normalized = _normalize_text(filename_stem)

    if not query_normalized or not filename_normalized:
        return 0

    # ---------------------------------------------------------
    # Exact title match
    # ---------------------------------------------------------

    if query_normalized == filename_normalized:
        return 1000

    query_keywords = _get_keywords(query)
    filename_keywords = _get_keywords(filename_stem)

    # ---------------------------------------------------------
    # Full query contained in filename
    # ---------------------------------------------------------

    if query_normalized in filename_normalized:
        extra_keywords = _count_extra_keywords(
            query_keywords,
            filename_keywords,
        )
        unwanted_count = _count_unwanted_markers(filename_stem)

        score = 900

        if extra_keywords > 0:
            score -= min(80, extra_keywords * 25)

        if unwanted_count > 0:
            score -= min(250, unwanted_count * 65)

        return max(score, 350)

    if not query_keywords or not filename_keywords:
        return 0

    matched_count = 0
    fuzzy_count = 0

    # ---------------------------------------------------------
    # Word-by-word matching
    # ---------------------------------------------------------

    for query_word in query_keywords:

        best_similarity = 0
        exact_match = False
        partial_match = False

        for filename_word in filename_keywords:

            # Exact word match
            if query_word == filename_word:

                exact_match = True
                break

            # Partial word match
            if (
                query_word in filename_word
                or filename_word in query_word
            ):

                partial_match = True
                break

            # Fuzzy word similarity
            similarity = difflib.SequenceMatcher(
                None,
                query_word,
                filename_word,
            ).ratio()

            if similarity > best_similarity:
                best_similarity = similarity

        if exact_match or partial_match:

            matched_count += 1

        elif best_similarity >= 0.75:

            matched_count += 1
            fuzzy_count += 1

    total_keywords = len(query_keywords)
    extra_keywords = _count_extra_keywords(
        query_keywords,
        filename_keywords,
    )
    unwanted_count = _count_unwanted_markers(filename_stem)

    # ---------------------------------------------------------
    # Strong keyword matches
    # ---------------------------------------------------------

    if matched_count == total_keywords:

        base_score = 780 if fuzzy_count > 0 else 850

        if extra_keywords > 0:
            base_score -= min(60, extra_keywords * 15)

        if unwanted_count > 0:
            base_score -= min(220, unwanted_count * 55)

        return max(base_score, 250)

    # ---------------------------------------------------------
    # Multiple keyword matches
    # ---------------------------------------------------------

    if matched_count >= 2:

        base_score = 650

        if extra_keywords > 0:
            base_score -= min(50, extra_keywords * 15)

        if unwanted_count > 0:
            base_score -= min(180, unwanted_count * 45)

        return max(base_score, 250)

    # ---------------------------------------------------------
    # Single keyword match
    # ---------------------------------------------------------

    if matched_count == 1:

        base_score = 500

        if extra_keywords > 0:
            base_score -= min(40, extra_keywords * 10)

        if unwanted_count > 0:
            base_score -= min(120, unwanted_count * 30)

        return max(base_score, 150)

    # ---------------------------------------------------------
    # Overall fuzzy matching
    # ---------------------------------------------------------

    similarity = difflib.SequenceMatcher(
        None,
        query_normalized,
        filename_normalized,
    ).ratio()

    return int(similarity * 700)


def score_file(query, file_info):
    """
    Calculate the final score for a file.

    Season and episode information are handled separately from
    the filename title.
    """

    filename_stem = file_info["stem_lower"]
    filename_extension = file_info.get("extension", "")

    query_season, query_episode = extract_episode_info(
        query
    )

    filename_season, filename_episode = extract_episode_info(
        filename_stem
    )

    # ---------------------------------------------------------
    # Episode matching
    # ---------------------------------------------------------

    if query_season is not None:

        if filename_season != query_season:
            return 0

    if query_episode is not None:

        if filename_episode != query_episode:
            return 0

    # ---------------------------------------------------------
    # Remove episode information before title matching
    # ---------------------------------------------------------

    clean_query = remove_episode_info(query)

    clean_filename = remove_episode_info(
        filename_stem
    )

    score = score_title(
        clean_query,
        clean_filename,
    )

    # Episode-only queries can have an empty title after
    # removing the episode information.
    if score <= 0:

        if query_episode is not None:

            score = 500

        else:

            return 0

    # ---------------------------------------------------------
    # Episode match bonus
    # ---------------------------------------------------------

    if (
        query_season is not None
        or query_episode is not None
    ):

        score += 200

    # ---------------------------------------------------------
    # Unwanted file types and markers
    # ---------------------------------------------------------

    if filename_extension in _SUBTITLE_EXTENSIONS:
        score -= 300

    if _count_unwanted_markers(filename_stem) > 0:
        score -= min(220, _count_unwanted_markers(filename_stem) * 55)

    # ---------------------------------------------------------
    # Preferred file format bonus
    # ---------------------------------------------------------

    preferred_extensions = {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".webm",
        ".mp3",
        ".wav",
        ".flac",
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pptx",
        ".ppt",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
    }

    if filename_extension in preferred_extensions:
        score += 25

    return score