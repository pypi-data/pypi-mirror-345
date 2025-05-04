def sanitize_filename(
    filename: str
) -> str:
    """
    Check the provided 'filename' and transform any backslash
    character into a normal slash ('/'), returning the new
    string.
    """
    return (
        filename.replace('\\', '/')
        if '\\' in filename else
        filename
    )