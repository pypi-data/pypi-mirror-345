from os import system
from sys import stdout
from time import sleep

system("")
ESC = "\x1B"

class Fg:
    black = f"{ESC}[30m"
    red = f"{ESC}[31m"
    green = f"{ESC}[32m"
    yellow = f"{ESC}[33m"
    blue = f"{ESC}[34m"
    magenta = f"{ESC}[35m"
    cyan = f"{ESC}[36m"
    white = f"{ESC}[37m"
    def rgb(r, g, b): return f"{ESC}[38;2;{r};{g};{b}m"


class Bg:
    black = f"{ESC}[40m"
    red = f"{ESC}[41m"
    green = f"{ESC}[42m"
    yellow = f"{ESC}[43m"
    blue = f"{ESC}[44m"
    magenta = f"{ESC}[45m"
    cyan = f"{ESC}[46m"
    white = f"{ESC}[47m"
    def rgb(r, g, b): return f"{ESC}[48;2;{r};{g};{b}m"


class Style:
    resetall = f"{ESC}[0m"
    bold = f"{ESC}[1m"
    dim = faint = f"{ESC}[2m"
    italic = f"{ESC}[3m"
    underline = f"{ESC}[4m"
    inverse = reverse = f"{ESC}[7m"
    strikethrough = f"{ESC}[9m"
    clear = f"{ESC}[2J"
    clearline = f"{ESC}[2K"


class Cursor:
    invisible = hide = f"{ESC}[?25l"
    visible = show = f"{ESC}[?25h"

    up = f"{ESC}[1A"
    down = f"{ESC}[1B"
    right = f"{ESC}[1C"
    left = f"{ESC}[1D"
    #nextline = f"{ESC}[1E"
    #prevline = f"{ESC}[1F"
    nextline = "\n"
    prevclearline = "\b"
    top = f"{ESC}[0;0H"
    #!bottom = f"{ESC}[0;0H"
    #savepostion = f"{ESC}[{s}"
    #restorelast = f"{ESC}[{u}"
    def to(x, y):
        return f"{ESC}[{y};{x}H"
    def toreplace(x, y):
        return Cursor.to(x,y)+Screen.clearline


class Screen:
    clearall = f"{ESC}[2J{ESC}[H"
    clearline = f"{ESC}[2K"

def strcolor(color: str, ignore_error=False):
    fgcolors = {
        "black": Fg.black,
        "red": Fg.red,
        "green": Fg.green,
        "yellow": Fg.yellow,
        "blue": Fg.blue,
        "magenta": Fg.magenta,
        "cyan": Fg.cyan,
        "white": Fg.white
    }
    color = color.lower()
    if color in fgcolors:
        return fgcolors[color]
    else:
        try:
            r, g, b = color.replace("r", "!").replace("g", "!").replace("b", "!").split('!')
            r, g, b = int(r), int(g), int(b)
            return Fg.rgb(r, g, b)
        except:
            if ignore_error:
                return color
            else:
                raise ValueError(f"String \'{color}\' doesn't represents any color.")

def strbackcolor(color: str, ignore_error=False):
    bgcolors = {
        "black": Bg.black,
        "red": Bg.red,
        "green": Bg.green,
        "yellow": Bg.yellow,
        "blue": Bg.blue,
        "magenta": Bg.magenta,
        "cyan": Bg.cyan,
        "white": Bg.white
    }
    color = color.lower()
    if color in bgcolors:
        return bgcolors[color]
    else:
        try:
            r, g, b = color.replace("r", "!").replace("g", "!").replace("b", "!").split('!')
            r, g, b = int(r), int(g), int(b)
            return Bg.rgb(r, g, b)
        except:
            if ignore_error:
                return color
            else:
                raise ValueError(f"String \'{color}\' doesn't represents any color.")
            
def write(text="\n", time=0.0):
    text = str(text)
    if time <= 0 or time == float('inf'):
        stdout.write(text)
        stdout.flush()
    else:
        t = time/len(text)
        for l in text:
            stdout.write(l)
            stdout.flush()
            sleep(t)
