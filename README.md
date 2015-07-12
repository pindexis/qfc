# qfc
Quick Command-line File Completion

qfc is an alternative of shell complete which features real-time multi-directories matching: It matches against all tracked files in a cvs tracked directory, or up to a sepcific depth if the directory is not tracked.
This is useful, to avoid the burden of writing the whole path whenever you want to `cd` or `vim` a file, which is frequent espacielly if you use the terminal as your IDE(The terminal is the best IDE, remember!).

## Features:
- Real-time matching: Results are displayed while you type.
- Multi-directories && Context relevant matching: if you're in a cvs(git,mercurial) tracked directory, qfc will matches against your tracked(or new) files only. This is very useful to avoid 10000+ of dependency files to clutter up the results. 
- Enhanced Filtering/Sorting of matches.

## Usage:
- Ctrl-f : complete current word using qfc

## Installation:
- `git clone https://github.com/pindexis/qfc $HOME/.qfc`
- Add the following line to your *.rc :  
    `[[ -s "$HOME/.qfc/bin/qfc.sh" ]] && source "$HOME/.qfc/bin/qfc.sh"`
