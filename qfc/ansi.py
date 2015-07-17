import sys

BOLD = "\x1b[1m"
CLEAR_FORMATTING = "\x1b[0m"
ERASE_SCREEN = "\x1b[J"
ERASE_LINE = "\x1b[2K"
FOREGROUND_BLACK = "\x1b[30m"
BACKGROUND_WHITE = "\x1b[47m"

def _CURSOR_COLUMN(pos):
    # ideally, CSI n G escape code is used to set the absolute horizental position
    # Sadly, it's not an Ansi.sys escape code (not supported in all terminals)
    # This shim try to simulate it by moving cursor backwards 1000 characters(terminal row width is assumed to be less than that number, which may not be the case for aliens laptops :))
    # Then, move cursor pos - 1 characthers forward (the - 1 is because the cursor is at position 1) 
    c = "\x1b[1000D"
    if pos:
        c += "\x1b["+str(pos - 1)+"C"
    return c

def _CURSOR_PREVIOUS_LINES(number):
    return "\x1b["+str(number)+"A"

def _CURSOR_NEXT_LINES(number):
    return "\x1b["+str(number)+"B"

def select_text(text):
    return  (FOREGROUND_BLACK +
            BACKGROUND_WHITE + 
            text.replace(
                CLEAR_FORMATTING,
                CLEAR_FORMATTING + FOREGROUND_BLACK + BACKGROUND_WHITE)+
            CLEAR_FORMATTING)

def bold_text(text):
    return  (BOLD + 
            text.replace(
                CLEAR_FORMATTING,
                CLEAR_FORMATTING + BOLD)+
            CLEAR_FORMATTING)

def move_cursor_line_beggining():
    sys.stdout.write(_CURSOR_COLUMN(0))

def move_cursor_horizental(n):
    sys.stdout.write(_CURSOR_COLUMN(n))

def move_cursor_previous_lines(number_of_lines):
    sys.stdout.write(_CURSOR_PREVIOUS_LINES(number_of_lines))

def move_cursor_next_lines(number_of_lines):
    sys.stdout.write(_CURSOR_NEXT_LINES(number_of_lines))

def erase_from_cursor_to_end():
    sys.stdout.write(ERASE_SCREEN)

def erase_line():
    sys.stdout.write(ERASE_LINE)

def flush():
    sys.stdout.flush()
