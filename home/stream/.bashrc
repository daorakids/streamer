# ~/.bashrc completo para o projeto Daora Kids

# Configurações padrão do Bash
case $- in
    *i*) ;;
      *) return;;
esac

HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s checkwinsize

# Identificação do chroot
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# Configuração de cores e prompt
force_color_prompt=yes
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    else
        color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\] '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# Aliases padrão
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# =================================================
# ATALHOS DAORA KIDS
# =================================================
alias ver="/home/stream/ver_live.sh"
alias monitor="/home/stream/ver_live.sh"

# Painel de Controle - Daora Kids (Melhorado com o alias 'ver')
clear
cat << 'EOF'
  ____                          _  ___     _      
 |  _ \  __ _  ___  _ __ __ _  | |/ (_) __| |___  
 | | | |/ _` |/ _ \| '__/ _` | | ' /| |/ _` / __| 
 | |_| | (_| | (_) | | | (_| | | . \| | (_| \__ \ 
 |____/ \__,_|\___/|_|  \__,_| |_|\_\_|\__,_|___/ 
                                                   
EOF
echo "================================================="
echo " 📺 PAINEL DE CONTROLE - DAORA KIDS 24H "
echo "================================================="
echo "▶ DIGITE: 'ver' ou 'monitor' para ver a live agora."
echo "▶ DICA: Pressione Ctrl+C para liberar o terminal."
echo "-------------------------------------------------"
echo " "

# Inicia o monitor automaticamente ao logar
/home/stream/ver_live.sh