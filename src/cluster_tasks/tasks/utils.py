def human_readable_size(size_in_bytes):
    """
    Converts a size in bytes to a human-readable format.

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Human-readable size.
    """
    if size_in_bytes is None:
        return "Unknown"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_in_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"
