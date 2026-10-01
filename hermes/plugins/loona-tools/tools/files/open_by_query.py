import json

from .episodes import extract_episode_info
from .open import loona_open_file
from .search import loona_search_files


def loona_open_file_by_query(args: dict, **kwargs) -> str:
    """
    Find and open the best matching local file.

    TV episode requests receive strict season/episode matching.
    """

    query = str(
        args.get("query", "")
    ).strip()

    if not query:

        return json.dumps({
            "success": False,
            "action": "search_failed",
            "error": "No file name was provided.",
        })

    # ---------------------------------------------------------
    # Detect TV episode request
    # ---------------------------------------------------------

    season, episode = extract_episode_info(query)

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    search_result = json.loads(
        loona_search_files({
            "query": query,
            "max_results": 10,
        })
    )

    if not search_result.get("success"):

        return json.dumps({
            "success": False,
            "action": "search_failed",
            "query": query,
            "index_status": search_result.get("index_status", "unknown"),
            "error": search_result.get(
                "error",
                "File search failed.",
            ),
        })

    results = search_result.get(
        "results",
        [],
    )

    # ---------------------------------------------------------
    # Nothing found
    # ---------------------------------------------------------

    if not results:

        return json.dumps({
            "success": False,
            "action": "not_found",
            "query": query,
            "index_status": search_result.get("index_status", "unknown"),
            "error": (
                f"No local file matching '{query}' "
                "was found on D: or E:."
            ),
        })

    # ---------------------------------------------------------
    # TV episode filtering
    # ---------------------------------------------------------

    if season is not None or episode is not None:

        episode_results = []

        for result in results:

            file_season, file_episode = extract_episode_info(
                result.get("name", "")
            )

            # If a season was requested, it must match.
            if season is not None and file_season != season:
                continue

            # If an episode was requested, it must match.
            if episode is not None and file_episode != episode:
                continue

            episode_results.append(result)

        results = episode_results

        if not results:

            if season is not None:

                error_message = (
                    f"No local file for Season {season}, "
                    f"Episode {episode} was found."
                )

            else:

                error_message = (
                    f"No local file for Episode {episode} "
                    "was found."
                )

            return json.dumps({
                "success": False,
                "action": "not_found",
                "query": query,
                "index_status": search_result.get("index_status", "unknown"),
                "error": error_message,
            })

    # ---------------------------------------------------------
    # Sort strongest match first
    # ---------------------------------------------------------

    results.sort(
        key=lambda item: item.get(
            "match_score",
            0,
        ),
        reverse=True,
    )

    best_match = results[0]

    # ---------------------------------------------------------
    # Safety threshold
    # ---------------------------------------------------------

    if best_match.get(
        "match_score",
        0,
    ) < 450:

        return json.dumps({
            "success": False,
            "action": "confirmation_required",
            "query": query,
            "index_status": search_result.get("index_status", "unknown"),
            "message": (
                "A weak local filename match was found. "
                "Do not open it automatically."
            ),
            "best_match": best_match,
        })

    # ---------------------------------------------------------
    # Check for competing matches
    # ---------------------------------------------------------

    if len(results) > 1:

        second_match = results[1]

        score_difference = (
            best_match.get("match_score", 0)
            - second_match.get("match_score", 0)
        )

        # If two results are very close, don't guess.
        if score_difference < 50:

            return json.dumps({
                "success": False,
                "action": "multiple_matches",
                "query": query,
                "index_status": search_result.get("index_status", "unknown"),
                "message": (
                    "Multiple local files are strong matches. "
                    "Do not open one automatically."
                ),
                "matches": results[:5],
            })

    # ---------------------------------------------------------
    # Open selected file
    # ---------------------------------------------------------

    open_result = json.loads(
        loona_open_file({
            "path": best_match["path"],
        })
    )

    if not open_result.get("success"):

        return json.dumps({
            "success": False,
            "action": "open_failed",
            "query": query,
            "selected_file": best_match,
            "index_status": search_result.get("index_status", "unknown"),
            "error": open_result.get(
                "error",
                "The file could not be opened.",
            ),
        })

    # ---------------------------------------------------------
    # Successful result
    # ---------------------------------------------------------

    return json.dumps({
        "success": True,
        "action": "opened",
        "query": query,
        "file": best_match["name"],
        "path": best_match["path"],
        "index_status": search_result.get("index_status", "unknown"),
        "message": (
            f"Successfully opened '{best_match['name']}'."
        ),
    })