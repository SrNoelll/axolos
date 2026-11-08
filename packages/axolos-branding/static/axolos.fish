# AxolOS · prompt y colores de fish para todos los usuarios
if status is-interactive
    if type -q starship; and not set -q AXOLOS_NO_STARSHIP
        starship init fish | source
    end
    set -q fish_color_command[1]; or set -g fish_color_command a69afe
    set -q fish_color_quote[1]; or set -g fish_color_quote 7ddfb4
    set -q fish_color_error[1]; or set -g fish_color_error ff7a93
    set -q fish_color_autosuggestion[1]; or set -g fish_color_autosuggestion 5a5a66
end
