import json
import os
import time


SEARCH_ROOTS = [
    "D:\\",
    "E:\\",
]


IGNORED_DIRECTORIES = {
    "$recycle.bin",
    "system volume information",
    "windowsapps",
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
}


PREFERRED_EXTENSIONS = {
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


_FILE_INDEX = None
_FILE_INDEX_STATUS = {
    "status": "missing",
    "refreshed": False,
    "inaccessible_directories": [],
}

INDEX_FILE = os.path.join(
    os.path.dirname(__file__),
    ".file_index.json",
)
INDEX_TTL_SECONDS = 300
INDEX_VERSION = 1


def _scan_drives():
    """
    Scan the D: and E: drives and build the file index.

    The scan keeps going even if one directory cannot be read. This allows the
    rest of the index to remain useful while recording the inaccessible path.
    """

    files_index = []
    inaccessible_directories = []

    def on_walk_error(error):
        path = getattr(error, "filename", None) or "<unknown>"
        message = getattr(error, "strerror", None) or str(error)
        inaccessible_directories.append({
            "path": path,
            "error": message,
        })

    for root in SEARCH_ROOTS:

        if not os.path.exists(root):
            continue

        for current_root, directories, files in os.walk(
            root,
            topdown=True,
            onerror=on_walk_error,
        ):

            directories[:] = [
                directory
                for directory in directories
                if directory.lower() not in IGNORED_DIRECTORIES
            ]

            try:
                os.listdir(current_root)
            except OSError as exc:
                inaccessible_directories.append({
                    "path": current_root,
                    "error": str(exc),
                })
                directories[:] = []
                continue

            for filename in files:

                full_path = os.path.join(
                    current_root,
                    filename,
                )

                name_without_extension = os.path.splitext(
                    filename
                )[0]

                files_index.append({
                    "name": filename,
                    "name_lower": filename.lower(),
                    "stem_lower": name_without_extension.lower(),
                    "path": full_path,
                    "extension": os.path.splitext(filename)[1].lower(),
                })

    return files_index, inaccessible_directories


def _save_index(files_index, inaccessible_directories=None):
    """
    Save the file index to disk, including scan metadata and any inaccessible
    directories encountered during indexing.
    """

    payload = {
        "version": INDEX_VERSION,
        "scanned_at": time.time(),
        "roots": SEARCH_ROOTS,
        "files": files_index,
        "inaccessible_directories": inaccessible_directories or [],
    }

    try:

        with open(
            INDEX_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                ensure_ascii=False,
            )

    except (OSError, TypeError):
        pass


def _load_index():
    """
    Load the previously saved file index.
    """

    if not os.path.exists(INDEX_FILE):
        return None

    try:

        with open(
            INDEX_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, dict) and isinstance(data.get("files"), list):
            return data

        if isinstance(data, list):
            return {
                "version": INDEX_VERSION,
                "scanned_at": time.time(),
                "roots": SEARCH_ROOTS,
                "files": data,
                "inaccessible_directories": [],
            }

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        pass

    return None


def _is_index_fresh(index_data):
    """Return True when the cached index is still valid for quick reuse."""

    if not isinstance(index_data, dict):
        return False

    scanned_at = float(index_data.get("scanned_at", 0) or 0)
    if time.time() - scanned_at <= INDEX_TTL_SECONDS:
        return True

    roots = index_data.get("roots", SEARCH_ROOTS)
    newest_root_mtime = 0.0

    for root in roots:
        try:
            newest_root_mtime = max(newest_root_mtime, os.path.getmtime(root))
        except OSError:
            continue

    return newest_root_mtime <= scanned_at


def get_file_index_status():
    """Expose the current index freshness state to the calling search layer."""

    return dict(_FILE_INDEX_STATUS)


def build_file_index():
    """
    Load a cached file index when it is still current.

    When the cache is stale, or the filesystem changed since the last scan, the
    index is refreshed automatically without requiring the user to delete the
    cache file manually.
    """

    global _FILE_INDEX, _FILE_INDEX_STATUS

    if _FILE_INDEX is not None:
        return _FILE_INDEX

    cached_index = _load_index()

    if cached_index is not None and _is_index_fresh(cached_index):
        _FILE_INDEX = cached_index.get("files", [])
        _FILE_INDEX_STATUS = {
            "status": "fresh",
            "refreshed": False,
            "inaccessible_directories": cached_index.get(
                "inaccessible_directories",
                [],
            ),
        }
        return _FILE_INDEX

    start_time = time.perf_counter()

    _FILE_INDEX, inaccessible = _scan_drives()
    _save_index(_FILE_INDEX, inaccessible)

    elapsed = time.perf_counter() - start_time

    _FILE_INDEX_STATUS = {
        "status": "refreshed" if cached_index is not None else "built",
        "refreshed": True,
        "inaccessible_directories": inaccessible,
    }

    print(
        f"[Loona] File index { _FILE_INDEX_STATUS['status'] }: "
        f"{len(_FILE_INDEX)} files "
        f"in {elapsed:.2f}s"
    )

    return _FILE_INDEX


def refresh_file_index():
    """
    Completely rebuild the file index.

    Use this when files have been added, removed, or moved and Loona needs to
    update its index.
    """

    global _FILE_INDEX, _FILE_INDEX_STATUS

    start_time = time.perf_counter()

    _FILE_INDEX, inaccessible = _scan_drives()
    _save_index(_FILE_INDEX, inaccessible)

    elapsed = time.perf_counter() - start_time

    _FILE_INDEX_STATUS = {
        "status": "refreshed",
        "refreshed": True,
        "inaccessible_directories": inaccessible,
    }

    print(
        f"[Loona] File index refreshed: "
        f"{len(_FILE_INDEX)} files "
        f"in {elapsed:.2f}s"
    )

    return _FILE_INDEX


def clear_file_index():
    """
    Remove the cached index from memory and disk.
    """

    global _FILE_INDEX, _FILE_INDEX_STATUS

    _FILE_INDEX = None
    _FILE_INDEX_STATUS = {
        "status": "missing",
        "refreshed": False,
        "inaccessible_directories": [],
    }

    try:

        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)

    except OSError:
        pass