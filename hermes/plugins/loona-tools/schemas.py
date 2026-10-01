GET_DATETIME = {
    "name": "get_datetime",
    "description": "Gets the current date, time, and timezone directly from the user's Windows PC.",
    "parameters": {
        "type": "object",
        "properties": {
            "include_timezone": {
                "type": "boolean",
                "description": "Whether to include the timezone information.",
                "default": True,
            }
        },
        "required": [],
    },
}


GET_SYSTEM_INFO = {
    "name": "get_system_info",
    "description": "Gets basic hardware and operating system information directly from the user's Windows PC, including CPU, RAM, GPU, Windows version, architecture, and disk space.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


LOONA_SEARCH_FILES = {
    "name": "loona_search_files",
    "description": (
        "PRIMARY TOOL FOR LOCAL COMPUTER FILE REQUESTS. "
        "Use this tool FIRST whenever the user asks to find, locate, search for, "
        "look for, or identify a file that may be stored on their Windows PC. "
        "This includes PDFs, theses, documents, Word files, Excel files, movies, "
        "videos, songs, images, applications, and other local files. "
        "Searches the user's LOCAL Windows PC on the D: and E: drives. "
        "Examples: 'find my thesis', 'find this PDF', 'find my bird recognition thesis', "
        "'find Avengers', 'locate my project', 'find that image'. "
        "These requests mean SEARCH THE USER'S COMPUTER, not the internet. "
        "DO NOT use web search for these requests. "
        "Only use web search when the user explicitly asks to search the internet, "
        "online, websites, academic databases, or other remote sources. "
        "Supports partial names and small spelling mistakes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name or keywords of the local file the user wants to find. "
                    "For example: 'World War Z', 'Avngers', 'thesis', or 'vacation'."
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of matching files to return.",
                "default": 10,
            },
        },
        "required": ["query"],
    },
}


LOONA_SEARCH_APPLICATIONS = {
    "name": "loona_search_applications",
    "description": (
        "Searches the user's Windows PC for installed applications. "
        "Use this when the user asks to find, locate, or identify an "
        "application installed on their PC. "
        "Do not use web search for installed application requests."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name of the Windows application to find. "
                    "Examples: Chrome, VS Code, Discord, VLC, Spotify."
                ),
            },
        },
        "required": ["query"],
    },
}

LOONA_OPEN_APPLICATION = {
    "name": "loona_open_application",
    "description": (
        "Opens a Windows application using a verified executable path "
        "returned by loona_search_applications."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "The full executable path of the application "
                    "returned by loona_search_applications."
                ),
            },
        },
        "required": ["path"],
    },
}


LOONA_CLOSE_APPLICATION = {
    "name": "loona_close_application",
    "description": (
        "Closes a running Windows application gracefully. "
        "Use this tool whenever the user asks to close an application. "
        "If a specific window or media item is mentioned, use the "
        "window_title parameter to target only that instance. "
        "Attempt a normal graceful close and verify that the targeted "
        "application instance exited. "
        "NEVER use terminal, PowerShell, CMD, taskkill, or another "
        "shell command to close the application. "
        "NEVER force terminate an application. "
        "If the targeted application cannot be closed gracefully, "
        "report the failure to the user instead of using another method."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "process_name": {
                "type": "string",
                "description": (
                    "The executable process name of the application, "
                    "such as PotPlayerMini64.exe, chrome.exe, "
                    "or notepad.exe."
                ),
            },
            "window_title": {
                "type": "string",
                "description": (
                    "Optional specific window title or distinctive "
                    "text from the window title to identify the exact "
                    "application instance to close. Use this when the "
                    "user refers to a specific movie, document, window, "
                    "or application instance."
                ),
            },
        },
        "required": ["process_name"],
    },
}


LOONA_OPEN_FILE = {
    "name": "loona_open_file",
    "description": (
        "Opens a specific LOCAL file on the user's Windows PC. "
        "Use this when an exact local file path is already known. "
        "Do NOT use web search for local files."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The exact local Windows file path.",
            },
        },
        "required": ["path"],
    },
}


LOONA_OPEN_FILE_BY_QUERY = {
    "name": "loona_open_file_by_query",
    "description": (
        "OPENS a LOCAL file on the user's Windows PC by searching the D: and E: "
        "drives and opening the best matching result. Use this tool whenever the "
        "user asks to open, launch, play, watch, or view a local file, movie, TV "
        "episode, video, song, document, image, or other file by name or "
        "description. This tool is the PRIMARY method for opening local files. Do "
        "NOT use execute_code, Python, shell commands, or manual filesystem "
        "scanning to search D:, E:, or C: for these requests. Examples: 'open "
        "World War Z', 'play Avengers', 'open my thesis', 'open that video', "
        "'play season 2 episode 5'. This is specifically for files stored on the "
        "user's PC. Do NOT use web search for these requests."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name or keywords of the local file, movie, video, song, "
                    "document, image, or other file the user wants to open."
                ),
            },
        },
        "required": ["query"],
    },
}

LOONA_SET_VOLUME = {
    "name": "loona_set_volume",
    "description": "Sets the Windows master volume to the requested percentage.",
    "parameters": {
        "type": "object",
        "properties": {
            "volume": {
                "type": "number",
                "description": "Volume percentage from 0 to 100.",
            },
        },
        "required": ["volume"],
    },
}