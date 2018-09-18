# default key bindings
complete_shortcut="${qfc_complete_SHORTCUT:-\C-f}"

function get_cursor_position(){
  # based on a script from http://invisible-island.net/xterm/xterm.faq.html
  exec < /dev/tty
  oldstty=$(stty -g)
  stty raw -echo min 0
  # on my system, the following line can be replaced by the line below it
  echo -en "\033[6n" > /dev/tty
  # tput u7 > /dev/tty    # when TERM=xterm (and relatives)
  IFS=';' read -r -d R  row col
  stty $oldstty
  # change from one-based to zero based so they work with: tput cup $row $col
  row=$((${row:2} - 1))    # strip off the esc-[
  col=$((${col} - 1))
  echo "$row $col"
}

# Determine the absolute path to the QFC script.
if [[ -n "$BASH_VERSION" ]]; then
  # Bash doesn’t evaluate $0 the right way when the script is sourced;
  # use $BASH_SOURCE instead.
  QFC=$(realpath $(dirname ${BASH_SOURCE[0]}))/qfc
else
  # In zsh, $0 is consistent between sourcing and script invocation.
  QFC=$(realpath $(dirname $0))/qfc
fi

if [[ -n "$ZSH_VERSION" ]]; then
    # zshell
    function qfc_complete {
        # Add a letter and remove it from the buffer.
        # when using zsh autocomplete(pressing Tab), then running qfc, the BUFFER(qfc input) won't contain the trailing forward slash(which should happen when using zsh autocomplete for directories).
        # pressing a character then removing it makes sure that BUFFER contains what you see on the screen.
        BUFFER=${BUFFER}'a'
        BUFFER=${BUFFER[0,-2]}
        # get the cursor offset within the user input
        offset=${CURSOR}
        zle beginning-of-line
        # get the offset from the start of comandline prompt
        col=$(echo $(get_cursor_position) | cut -f 2 -d " ")
        # place the cursor at the next line
        </dev/tty echo ''

        # get the word under cursor
        word=${BUFFER[0,offset]}
        word=${word##* }

        # instruct qfc to store the result (completion path) into a temporary file
        tmp_file=$(mktemp -t qfc.XXXXXXX)
        </dev/tty "$QFC" --search="$word" --stdout="$tmp_file"
        result=$(<$tmp_file)
        rm -f $tmp_file

        # append the completion path to the user buffer
        word_length=${#word}
        result_length=${#result}
        BUFFER=${BUFFER[1,$((offset-word_length))]}${result}${BUFFER[$((offset+word_length)),-1]}
        let "offset = offset - word_length + result_length"

        # reset the absolute and relative cursor position, note that it's necessary to get row position after qfc is run, because it may be changed during qfc execution
        row=$(echo $(get_cursor_position) | cut -f 1 -d " ")
        tput cup $(($row - 1)) $col
        CURSOR=${offset}
    }

    zle -N qfc_complete
    bindkey "$complete_shortcut" qfc_complete

    function qfc_quick_command(){
      if [[ ! -z $1 ]] && [[ ! -z $2 ]] && [[ ! -z $3 ]]; then
        func_name='quick_'$1
        eval $"function $func_name(){
          zle kill-whole-line
          qfc_complete
          if [[ ! -z \${BUFFER} ]]; then
            c='$3'
            BUFFER=\${c//'\$0'/\$BUFFER}
            zle accept-line
          fi
        }"
        zle -N $func_name
        bindkey "$2" $func_name
      fi
    }

elif [[ -n "$BASH" ]]; then

    function qfc_complete {
        # pretty similar to zsh flow
        offset=${READLINE_POINT}
        READLINE_POINT=0
        col=$(get_cursor_position | cut -f 2 -d " ")

        word=${READLINE_LINE:0:offset}
        word=${word##* }

        tmp_file=$(mktemp -t qfc.XXXXXXX)
        </dev/tty "$QFC" --search="$word" --stdout="$tmp_file"
        result=$(<$tmp_file)
        rm -f $tmp_file

        word_length=${#word}
        result_length=${#result}
        READLINE_LINE=${READLINE_LINE:0:$((offset-word_length))}${result}${READLINE_LINE:$((offset))}
        offset=$(($offset - $word_length + $result_length))

        row=$(get_cursor_position | cut -f 1 -d " ")
        tput cup $row $col
        READLINE_POINT=${offset}
    }

    bind -x '"'"$complete_shortcut"'":"qfc_complete"'

    function qfc_quick_command {
      if [[ ! -z $1 ]] && [[ ! -z $2 ]] && [[ ! -z $3 ]]; then
        func_name='quick_'$1
        eval $"function $func_name(){
          READLINE_LINE=''
          qfc_complete
          if [[ ! -z \${READLINE_LINE} ]]; then
            c='$3'
            READLINE_LINE=\${c//'\$0'/\$READLINE_LINE}
          fi
        }"
        bind -x '"\e-'"$1"'":"'"${func_name}"'"'
        bind '"'"$2"'":""\e-'"$1"'\n"'
      fi
    }

fi
