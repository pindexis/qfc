# qfc
Quick Command-line File Completion

![qfc](https://cloud.githubusercontent.com/assets/2557967/8640880/582cb8fe-28ff-11e5-9753-41464dda938e.gif)

qfc is a shell auto-complete alternative which features real-time multi-directories matching: It provides results  while you type against files in the current directory and its sub-directories.
This is useful, to avoid the burden of writing the whole path whenever you want to `cd` or `vim` a file, which is frequent especially if you use the terminal as your IDE(The terminal is the best IDE, remember! :-) ).


## Features:
- Real-time matching: Results are displayed while you type.
- Multi-directories && Context relevant matching: if you're in a cvs(git,mercurial) managed directory, qfc will matches against your tracked(or new) files only. This is very useful to avoid 10000+ of dependency files cluttering up the results. for unmanaged dirs, qfc looks for unhidden files up to a maximum depth(set to 3).
- Enhanced Filtering/Sorting of matches.
- No dependencies.


## Requirements
- python (2.7+ or 3.0+)
- Bash-4.0+ or Zshell.
- Linux Or OSX  
In OSX, it seems like Bash 3.x is the default shell which is not supported. you have to [update your Bash to 4.0+](http://apple.stackexchange.com/a/24635) or [change your shell to zshell](http://stackoverflow.com/a/1822126/1117720).


## Installation:
- `git clone https://github.com/pindexis/qfc $HOME/.qfc`
- Add the following line to your *rc (.zshrc, .bashrc, .bash_profile in OSX):  
    `[[ -s "$HOME/.qfc/bin/qfc.sh" ]] && source "$HOME/.qfc/bin/qfc.sh"`


## Usage:
- `Ctrl-f` : complete the word under cursor using qfc
- while qfc is open:
    - `TAB`: Append the selected match to the current path.
    - `ENTER`: Append the selected match to the current path and returns the result.
    - `Ctrl-f`: Returns the current path.
    - `Arrow keys`: Navigation between files.


## Even more Productivity:
If you're using zshell or Bash 4.3+, You can combine qfc with commands you frequently use to get one key-stroke experience. For example, I have the following lines in my .zshrc:
```
qfc_quick_command 'cd' '\C-b' 'cd $0'
qfc_quick_command 'vim' '\C-p' 'vim $0'
```
This allows me to switch directories by just pressing Ctrl-b(or editing a file by pressing Ctrl-p).
![qfc](https://cloud.githubusercontent.com/assets/2557967/8654777/78534320-2984-11e5-8684-f18709af0748.gif)

`qfc_quick_command` expects an `id`, `a shortcut`, and a command with `$0` placeholder(which will be replaced with the completion path).  
It's recommended to choose a 2-5 length letters only `id`(else you may encounter issues).  
Also, be careful with what keyboard shortcuts to choose(mapping some keys can prevent the terminal from working correctly).
