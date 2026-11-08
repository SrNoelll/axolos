# AxolOS · terminal para desarrollo (paquete axolos-dev)
# Desactívalo entero con:  set -U AXOLOS_NO_DEV_SHELL 1
if status is-interactive; and not set -q AXOLOS_NO_DEV_SHELL
    # fzf: Ctrl+T busca ficheros, Alt+C entra en carpetas (Ctrl+R lo lleva atuin)
    type -q fzf; and fzf --fish | source
    set -q FZF_DEFAULT_COMMAND; or set -gx FZF_DEFAULT_COMMAND 'fd --type f --hidden --exclude .git'
    set -q FZF_CTRL_T_COMMAND; or set -gx FZF_CTRL_T_COMMAND $FZF_DEFAULT_COMMAND
    set -q FZF_DEFAULT_OPTS; or set -gx FZF_DEFAULT_OPTS '--height 40% --layout reverse --border rounded --color=bg+:#1e1e26,fg+:#ffffff,hl:#a69afe,hl+:#cdc6ff,pointer:#a69afe,marker:#7ddfb4,prompt:#a69afe,info:#8a8a99,border:#4b4b57,spinner:#7fd4e4'

    # zoxide: "z proyecto" salta a la carpeta que más usas con ese nombre
    type -q zoxide; and not functions -q z; and zoxide init fish | source

    # atuin: historial con búsqueda en Ctrl+R (la flecha arriba sigue igual)
    type -q atuin; and atuin init fish --disable-up-arrow | source

    # direnv: carga el .envrc de cada proyecto al entrar
    type -q direnv; and direnv hook fish | source

    # mise: versiones de node/python/go… por proyecto (.mise.toml / .tool-versions)
    type -q mise; and mise activate fish | source

    # bat y delta con los colores de la terminal (paleta AxolOS)
    set -q BAT_THEME; or set -gx BAT_THEME ansi
end
