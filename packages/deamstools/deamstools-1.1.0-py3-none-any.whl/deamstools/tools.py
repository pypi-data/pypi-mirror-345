import time

def pretty_print(text, delay=0.05, end=True):
    for char in text:
        print(char, end='' ,flush=True)
        time.sleep(delay)
    print(end='\n' if end else '')

def reverse_pretty_print(text, delay=0.05, end=False):
    result = ""
    for char in reversed(text):
        result = char + result
        print('\r' + result, end='', flush=True)
        time.sleep(delay)
    print(end='\n' if end else '')



def rgb_text(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def rgb_gradient_text(start_color, end_color, text):
    def interpolate(start, end, factor):
        return int(start + (end - start) * factor)

    gradient_text = ""
    for i, char in enumerate(text):
        factor = i / (len(text) - 1) if len(text) > 1 else 0
        r = interpolate(start_color[0], end_color[0], factor)
        g = interpolate(start_color[1], end_color[1], factor)
        b = interpolate(start_color[2], end_color[2], factor)
        gradient_text += f"\033[38;2;{r};{g};{b}m{char}"
    gradient_text += "\033[0m"
    return gradient_text




