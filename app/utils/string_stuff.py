def script_header(string):
    """
    Generate a formatted script header.

    Args:
        string (str): The content to be included in the script header.

    Returns:
        str: A formatted string representing the script header.

    This function takes a string as input and formats it into a script header by
    capitalizing the input string, adding a colon, and placing it on a new line.

    Example:
        header = script_header("intro")
        print(header)
        # Output: "\nINTRO:"
    """
    return f"\n{string.upper()}:\n"
