import os
import re
from . import keys
from . import ui
from . import readchar
from . import dirhandler


def get_selected_command_or_input(search):
    state = State(search)
    # draw the screen (prompt + matched strings)
    ui.refresh(state)
    # wait for user input
    prompt(state)
    # clear the screen
    ui.erase()
    # state.input holds the path selected by the user
    return state.input


def prompt(state):
    while True:
        c = readchar.get_symbol()
        if c == keys.ENTER:
            if state.get_matches():
                state.append_match_to_input()
            break
        elif c == keys.CTRL_F:
            break
        elif c == keys.TAB:
            if state.get_matches():
                state.append_match_to_input()
        elif c == keys.CTRL_C or c == keys.ESC:
            state.reset_input()
            break
        elif c == keys.CTRL_U:
            state.clear_input()
        elif c == keys.BACKSPACE:
            state.set_input(state.input[0:-1])
        elif c == keys.UP or c == keys.CTRL_K:
            state.select_previous()
        elif c == keys.DOWN or c == keys.CTRL_J:
            state.select_next()
        elif c == keys.LEFT or c == keys.CTRL_H:
            state.go_back()
        elif c == keys.RIGHT or c == keys.CTRL_L:
            if state.get_matches():
                state.append_match_to_input()
        elif c < 256 and c >= 32:
            state.set_input(state.input + chr(c))
        ui.refresh(state)


class State(object):
    ''' The Current User state, including user written characters, matched commands, and selected one '''

    def __init__(self, default_input):
        self._selected_command_index = 0
        self.matches = []
        self.default_input = default_input
        self.set_input(default_input)

    def get_matches(self):
        return self.matches

    def reset_input(self):
        self.input = self.default_input

    def set_input(self, input):
        self.input = input if input else ""
        self._update()

    def append_match_to_input(self):
        self.set_input(os.path.join(os.path.dirname(self.input), self.get_selected_match()))

    def go_back(self):
        isdir = is_dir(self.input)
        input_stripped = self.input.rstrip(os.sep)
        if not input_stripped:
            return
        input_splitted = input_stripped.split(os.sep)
        entry_name = input_splitted[-1]
        if isdir:
            entry_name += os.sep
        new_input = os.sep.join(input_splitted[0:-1])
        if new_input:
            new_input += os.sep
        self.set_input(new_input)
        self.set_selected_entry(entry_name)

    def clear_input(self):
        self.set_input("")

    def clear_selection(self):
        self._selected_command_index = 0

    def select_next(self):
        self._selected_command_index = (self._selected_command_index + 1) % len(self.matches) if len(self.matches) else 0

    def select_previous(self):
        self._selected_command_index = (self._selected_command_index - 1) % len(self.matches) if len(self.matches) else 0

    def _update(self):
        self.matches = get_matches(os.getcwd(),self.input)
        self._selected_command_index = 0

    def get_output(self):
        return self.input

    def get_selected_match(self):
        if len(self.matches):
            return self.matches[self._selected_command_index]
        else:
            raise Exception('No matches found')

    def set_selected_entry(self, entry):
        if not (entry in self.matches):
            return
        self._selected_command_index = self.matches.index(entry)


def get_matches(root_dir, user_input):
    start_dir = join_paths(root_dir, os.path.dirname(user_input)) 
    search_str = os.path.basename(user_input)
    if not os.path.isdir(start_dir):
        return []
    source_files = dirhandler.get_source_files(start_dir)
    filtered_files = filter_files(source_files, search_str)
    sorted_files = sort_matches(filtered_files, search_str)
    return sorted_files


def filter_files(files, search_str):
    """ Filter a list of files based on a search string
        :param files: list of files to filter (ie ['/a','/a/b', '/a/b/c', '/b']), the order doesn't matter. 'a' and 'a/' are considered different.
        :param search_str, the filtering string (ie 'a')
        
        This function return only first level files/dirs that match the given search string. That is, filtering  ['/a','/a/b','/a/b/c'] with the string 'a' returns only ['/a'],
        This is to avoid polluting the screen with all files inside a directory when a user look for that directory
    """
    matched = set()
    if not search_str:
        for f in files:
            # right strip to the first seperator(ie '/')
            f = f[:_index_or_len(f, os.sep)+1]
            matched.add(f)
    else:
        search_str = search_str.lower()
        for f in files:
            if search_str in f.lower():
                index = f.lower().index(search_str)
                trail = f[index:]
                f = f[:index + _index_or_len(trail, os.sep)+1]
                matched.add(f)
    return matched

def sort_matches(matches, string):
    """ Sort paths according to a string """
    files = sorted(matches, key=lambda s: s.lower())
    return sorted(files, key=lambda p:get_weight(p, string))

def get_weight(path, string):
    """ calculate how much a path matches a given string on a scale of 0->10000, a lower number means a better match.
    The string should be present in the path, or this function will fail

    The weight is calculated using the following formula:
                                                    0  00  0
                                                    |  |   |
    Number of elements in the path <----------------|  |   |--------------------------> is a directory(0) or not(1)
    (ie 2 for 'aa/bb' and 3 for 'aa/bb/cc')            |
                                                       |
                                                       v
                        There is a word in the matched path element that exactly match the given string? ('aa_bb' matches user input 'aa' but doesn't match 'a')
                                                       |
                               No <--------------------|-----------------------------> yes
                                |                                                       |
                                |                                                       |
                                |                                                       |
                                v                                                       v
    path element starts with the user input?                    There is only one word in the matched path element ('aa' but not 'aa_bb'),
                       |                                             which means the path elements exactly match the string
                       |                                                                                    |
            No <-------|-----Yes(2)                                                                 No -----|----- Yes (0)
            |                                                                                       |
            v                                                                                       v
index of the string in the path element + 10                                 (index of the matched word within path element words + 1)
                                        

    Maximums are added to make sure things doesn't overlap
    """
    weight = 0
    if not is_dir(path):
        weight += 1 

    string = string.lower()
    p = path.rstrip(os.sep).lower()
    path_elems = p.split(os.sep)
    weight += min(len(path_elems) * 1000, 10000) # Max 10 elements in path(set it to 10 for longer paths)

    if not string:
        return weight

    elm = next(e for e in path_elems if string in e)
    elm_words = [_f for _f in re.split('[\W_]+', elm) if _f]
    if string in elm_words:
        if len(elm_words) > 1:
            weight += 10 * (min(elm_words.index(string),8) + 1) # Max 8 words per path entry
    else:
        if elm.startswith(string):
            weight += 10 * 2
        else:
            weight += 10 * (10 + min(elm.index(string), 89)) # Max path element with 89 characters
    return weight

# Helper functions:

def join_paths(p1, p2):
    p1 = (os.path.expandvars(os.path.expanduser(p1)))
    p2 = (os.path.expandvars(os.path.expanduser(p2)))
    return os.path.normpath(os.path.join(p1, p2))

def _index_or_len(s, c):
    if c in s:
        return s.index(c)
    else:
        return len(s)

def is_dir(p):
    if p.endswith(os.sep):
        return True
    return False
