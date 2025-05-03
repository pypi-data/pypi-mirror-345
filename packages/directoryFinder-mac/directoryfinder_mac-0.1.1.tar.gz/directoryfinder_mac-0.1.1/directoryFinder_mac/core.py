import os
import difflib

def fuzzy_match(user_input, choices, cutoff):
    """
    Finds the closest match to the user_input from choices using fuzzy logic.

    Args:
        user_input (str): The name to match.
        choices (list): A list of file/folder names to compare against.
        cutoff (float): Optional threshold between 0–1 for match confidence. Default is 0.6.

    Returns:
        str or None: Best match if found, else None.
    """
    best_match = difflib.get_close_matches(user_input, choices, n=1, cutoff=cutoff)
    return best_match[0] if best_match else None


def find_file_in_dirs(file_name, folder_names, cutoff=0.7):
    """
    Searches for a file or folder inside specified user folders (Desktop, Downloads, etc.).
    Uses fuzzy matching to find approximate names.

    Args:
        file_name (str): The name of the file or folder to search (case-insensitive).
        folder_names (list): Folder names relative to the user's home directory.
        cutoff (float): Optional threshold for fuzzy matching (default is 0.6).

    Returns:
        list: Absolute paths of matched files/folders.
    """
    if not folder_names or not isinstance(folder_names, list):
        raise ValueError("folder_names must be a non-empty list.")

    home = os.path.expanduser("~")
    normalized_input = file_name.strip().lower()
    matches = []

    search_dirs = [os.path.join(home, folder) for folder in folder_names]

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue

        for dirpath, dirnames, filenames in os.walk(search_dir):
            all_items = filenames + dirnames
            match = fuzzy_match(normalized_input, [item.lower() for item in all_items], cutoff=cutoff)
            if match:
                for item in all_items:
                    if item.lower() == match:
                        matches.append(os.path.join(dirpath, item))
                        break  # Avoid duplicates

    return matches


