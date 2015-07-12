# default key bindings
complete_shortcut="${QFC_COMPLETE_SHORTCUT:-\C-f}"

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

if [[ -n "$ZSH_VERSION" ]]; then

    DIR=$( cd "$( dirname "$0" )" && pwd )
    PATH=$DIR:$PATH

    # zshell
    function c_complete {
        offset=${CURSOR}
        zle beginning-of-line
        row=$(echo $(get_cursor_position) | cut -f 2 -d " ")
        col=$(echo $(get_cursor_position) | cut -f 1 -d " ")
        </dev/tty echo ''
#        tput cup $(expr $col + 1) $row
        word=${BUFFER[0,offset]}
        word=${word##* }

        tmp_file=$(mktemp -t qfc.XXXXXXX)
        </dev/tty qfc --search="$word" --stdout="$tmp_file"
        result=$(<$tmp_file)
        rm -f $tmp_file

        word_length=${#word}
        result_length=${#result}
        BUFFER=${BUFFER[1,$((offset-word_length))]}${result}${BUFFER[$((offset+word_length)),-1]}
        let "offset = offset - word_length + result_length"
        #position might have been changed
        col=$(echo $(get_cursor_position) | cut -f 1 -d " ")
        tput cup $(expr $col - 1) $row
        CURSOR=${offset}
    }

    zle -N c_complete 
    bindkey "$complete_shortcut" c_complete 

elif [[ -n "$BASH" ]]; then

    DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
    PATH=$DIR:$PATH

    function c_complete {
        offset=${READLINE_POINT}
        READLINE_POINT=0
        row=$(echo $(get_cursor_position) | cut -f 2 -d " ")
        word=${READLINE_LINE:0:offset}
        word=${word##* }

        tmp_file=$(mktemp -t qfc.XXXXXXX)
        </dev/tty qfc --search="$word" --stdout="$tmp_file"
        result=$(<$tmp_file)
        rm -f $tmp_file

        word_length=${#word}
        result_length=${#result}
        READLINE_LINE=${READLINE_LINE:0:$((offset-word_length))}${result}${READLINE_LINE:$((offset))}
        offset=$(expr $offset - $word_length + $result_length)
        #position might have been changed
        col=$(echo $(get_cursor_position) | cut -f 1 -d " ")
        tput cup $col $row
        READLINE_POINT=${offset}
    }

    bind -x '"'"$complete_shortcut"'":"c_complete"'
fi
