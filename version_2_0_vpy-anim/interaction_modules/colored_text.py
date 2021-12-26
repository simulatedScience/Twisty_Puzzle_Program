import colored

def colored_text(text, color):
    """
    return text to be printed in the given color

    inputs:
    -------
        text - (str) - any string
        color - (str) - a hex-code as a color (including '#') i.e. "#0055cc"

    returns:
    --------
        (str) - given text formatted with the given color
    """
    use_color = colored.fg(color)
    return f"{use_color}{text}{colored.attr('reset')}"