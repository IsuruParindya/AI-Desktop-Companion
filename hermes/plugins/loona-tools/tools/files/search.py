import json
import os

from .index import build_file_index, get_file_index_status
from .matching import (
    _get_keywords,
    _normalize_text,
    score_file,
)


def _get_candidate_files(query, file_index):
    """
    Quickly narrow the full file index down to likely candidates.

    Keep the candidate set broad enough that fuzzy title matching can still
    select the correct result even when a few ordinary query words are present.
    """

    normalized_query = _normalize_text(query)

    if not normalized_query:
        return []

    query_keywords = _get_keywords(normalized_query)

    # First try files whose normalized filename contains the complete query.
    direct_matches = []

    for file_info in file_index:

        filename = _normalize_text(file_info["stem_lower"])

        if normalized_query in filename:
            direct_matches.append(file_info)

    if direct_matches:
        return direct_matches

    # Otherwise, look for files containing at least one meaningful keyword.
    keyword_matches = []

    for file_info in file_index:

        filename = _normalize_text(file_info["stem_lower"])

        if any(
            keyword in filename
            for keyword in query_keywords
        ):
            keyword_matches.append(file_info)

    # Do not prematurely remove the rest of the file index. A weaker keyword
    # match can still be a worse candidate than a real fuzzy title match.
    if not keyword_matches:
        return file_index

    return list(dict.fromkeys(keyword_matches + file_index))


def loona_search_files(args: dict, **kwargs) -> str:
    """
    Search the user's D: and E: drives for local files.

    This tool is read-only.
    """

    query = str(
        args.get("query", "")
    ).strip()

    if not query:

        return json.dumps({
            "success": False,
            "error": "No search query was provided.",
            "results": [],
        })

    try:

        max_results = int(
            args.get("max_results", 10)
        )

    except (TypeError, ValueError):

        max_results = 10

    max_results = max(
        1,
        min(max_results, 20),
    )

    file_index = build_file_index()
    index_status = get_file_index_status()

    # ---------------------------------------------------------
    # Fast candidate filtering
    # ---------------------------------------------------------

    candidates_to_score = _get_candidate_files(
        query,
        file_index,
    )

    candidates = []

    # ---------------------------------------------------------
    # Detailed scoring
    # ---------------------------------------------------------

    for file_info in candidates_to_score:

        score = score_file(
            query,
            file_info,
        )

        if score <= 0:
            continue

        candidates.append(
            (
                score,
                file_info,
            )
        )

    # ---------------------------------------------------------
    # Sort strongest matches first
    # ---------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            -item[0],
            item[1]["name_lower"],
        )
    )

    # ---------------------------------------------------------
    # Build final results
    # ---------------------------------------------------------

    results = []
    seen_paths = set()

    for score, file_info in candidates:

        full_path = file_info["path"]

        normalized_path = os.path.normcase(
            os.path.normpath(full_path)
        )

        if normalized_path in seen_paths:
            continue

        seen_paths.add(normalized_path)

        results.append({
            "name": file_info["name"],
            "path": full_path,
            "match_score": score,
        })

        if len(results) >= max_results:
            break

    return json.dumps({
        "success": True,
        "query": query,
        "result_count": len(results),
        "index_status": index_status.get("status", "unknown"),
        "results": results,
    })