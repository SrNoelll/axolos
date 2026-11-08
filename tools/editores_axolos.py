#!/usr/bin/env python3
"""AxolOS · temas de editor a partir de UNA paleta (la de la terminal y el escritorio).

  editores_axolos.py DIR     genera en DIR:
      kate/axolos.theme                 Kate / KWrite / KDevelop (KSyntaxHighlighting)
      nvim/axolos.lua                   Neovim  (:colorscheme axolos)
      vscode/axolos-theme.vsix          VS Code, VSCodium, Antigravity…
"""
import json
import sys
import zipfile
from pathlib import Path

# --- Paleta AxolOS (misma que tools/terminal_axolos.py) -----------------------
P = dict(
    bg="#17171d", bg_dark="#0f0f13", bg_side="#131318", surface="#1e1e26", border="#26262f",
    fg="#e6e6ee", muted="#8a8a99", faint="#4b4b57", comment="#6e6c80",
    accent="#a69afe", accent_hi="#cdc6ff", accent_lo="#7662ce", indigo="#8f85f2", lilac="#b4acff",
    pink="#ff7a93", pink_hi="#ff9fb0", green="#7ddfb4", yellow="#f3cf7a", yellow_hi="#fbe2a6",
    cyan="#7fd4e4", white="#f3f3f8",
)
VERSION = "1.0.0"

# Papel de cada color en el código (común a los tres editores)
SYN = dict(
    keyword=P["accent"], control=P["accent"], function=P["cyan"], string=P["green"],
    number=P["pink_hi"], constant=P["pink_hi"], type=P["yellow"], operator=P["lilac"],
    preproc=P["indigo"], attribute=P["yellow_hi"], comment=P["comment"], variable=P["fg"],
    property=P["accent_hi"], builtin=P["lilac"], escape=P["yellow_hi"], tag=P["accent"],
    error=P["pink"], warning=P["yellow"],
)


# --- Kate (KSyntaxHighlighting) ----------------------------------------------
def kate():
    def st(color, **kw):
        d = {"text-color": color, "selected-text-color": color}
        d.update(kw)
        return d
    text = {
        "Normal": st(P["fg"]), "Keyword": st(SYN["keyword"]), "Function": st(SYN["function"]),
        "Variable": st(SYN["property"]), "ControlFlow": st(SYN["control"]), "Operator": st(SYN["operator"]),
        "BuiltIn": st(SYN["builtin"]), "Extension": st(SYN["type"]), "Preprocessor": st(SYN["preproc"]),
        "Attribute": st(SYN["attribute"]), "Char": st(SYN["string"]), "SpecialChar": st(SYN["escape"]),
        "String": st(SYN["string"]), "VerbatimString": st(SYN["string"]), "SpecialString": st(SYN["escape"]),
        "Import": st(SYN["preproc"]), "DataType": st(SYN["type"]), "DecVal": st(SYN["number"]),
        "BaseN": st(SYN["number"]), "Float": st(SYN["number"]), "Constant": st(SYN["constant"]),
        "Comment": st(SYN["comment"], italic=True), "Documentation": st(SYN["comment"], italic=True),
        "Annotation": st(SYN["attribute"]), "CommentVar": st(P["lilac"], italic=True),
        "RegionMarker": st(P["indigo"], **{"background-color": P["surface"]}),
        "Information": st(P["cyan"]), "Warning": st(SYN["warning"]),
        "Alert": st(P["pink"], bold=True), "Error": st(SYN["error"], underline=True), "Others": st(P["green"]),
    }
    editor = {
        "BackgroundColor": P["bg"], "CodeFolding": P["surface"], "BracketMatching": "#3a3360",
        "CurrentLine": "#1d1d25", "IconBorder": P["bg"], "IndentationLine": P["border"],
        "LineNumbers": P["faint"], "CurrentLineNumber": P["accent_hi"], "MarkBookmark": P["indigo"],
        "MarkBreakpointActive": P["pink"], "MarkBreakpointReached": P["yellow"],
        "MarkBreakpointDisabled": P["faint"], "MarkExecution": P["cyan"], "MarkWarning": P["yellow"],
        "MarkError": P["pink"], "ModifiedLines": P["yellow"], "ReplaceHighlight": "#24503d",
        "SavedLines": P["green"], "SearchHighlight": "#4a3f7a", "TextSelection": "#3a3360",
        "Separator": P["border"], "SpellChecking": P["pink"], "TabMarker": P["border"],
        "TemplateBackground": P["surface"], "TemplatePlaceholder": "#2a2540",
        "TemplateFocusedPlaceholder": "#3a3360", "TemplateReadOnlyPlaceholder": P["surface"],
        "WordWrapMarker": P["border"],
    }
    return json.dumps({"metadata": {"name": "AxolOS", "revision": 1, "license": "MIT",
                                    "author": "AxolOS"},
                       "text-styles": text, "editor-colors": editor, "custom-styles": {}}, indent=2)


# --- Neovim --------------------------------------------------------------------
def nvim():
    hl = {
        "Normal": dict(fg=P["fg"], bg=P["bg"]), "NormalFloat": dict(fg=P["fg"], bg=P["surface"]),
        "FloatBorder": dict(fg=P["accent_lo"], bg=P["surface"]), "Cursor": dict(fg=P["bg"], bg=P["accent"]),
        "CursorLine": dict(bg="#1d1d25"), "CursorLineNr": dict(fg=P["accent_hi"], bold=True),
        "LineNr": dict(fg=P["faint"]), "SignColumn": dict(bg=P["bg"]), "ColorColumn": dict(bg=P["surface"]),
        "Visual": dict(bg="#3a3360"), "Search": dict(fg=P["bg"], bg=P["accent"]),
        "IncSearch": dict(fg=P["bg"], bg=P["yellow"]), "MatchParen": dict(fg=P["accent_hi"], bg="#3a3360", bold=True),
        "Pmenu": dict(fg=P["fg"], bg=P["surface"]), "PmenuSel": dict(fg=P["white"], bg=P["accent_lo"]),
        "PmenuSbar": dict(bg=P["surface"]), "PmenuThumb": dict(bg=P["faint"]),
        "StatusLine": dict(fg=P["fg"], bg=P["bg_dark"]), "StatusLineNC": dict(fg=P["muted"], bg=P["bg_dark"]),
        "TabLine": dict(fg=P["muted"], bg=P["bg_dark"]), "TabLineSel": dict(fg=P["white"], bg=P["bg"]),
        "TabLineFill": dict(bg=P["bg_dark"]), "WinSeparator": dict(fg=P["border"]),
        "VertSplit": dict(fg=P["border"]), "Folded": dict(fg=P["muted"], bg=P["surface"]),
        "NonText": dict(fg=P["border"]), "Whitespace": dict(fg=P["border"]), "EndOfBuffer": dict(fg=P["bg"]),
        "Title": dict(fg=P["accent"], bold=True), "Directory": dict(fg=P["accent"]),
        "ErrorMsg": dict(fg=P["pink"]), "WarningMsg": dict(fg=P["yellow"]), "MoreMsg": dict(fg=P["green"]),
        "Question": dict(fg=P["cyan"]), "WildMenu": dict(fg=P["bg"], bg=P["accent"]),
        "Comment": dict(fg=SYN["comment"], italic=True), "Constant": dict(fg=SYN["constant"]),
        "String": dict(fg=SYN["string"]), "Character": dict(fg=SYN["string"]), "Number": dict(fg=SYN["number"]),
        "Boolean": dict(fg=SYN["constant"]), "Float": dict(fg=SYN["number"]),
        "Identifier": dict(fg=SYN["variable"]), "Function": dict(fg=SYN["function"]),
        "Statement": dict(fg=SYN["keyword"]), "Keyword": dict(fg=SYN["keyword"]),
        "Conditional": dict(fg=SYN["control"]), "Repeat": dict(fg=SYN["control"]),
        "Operator": dict(fg=SYN["operator"]), "Exception": dict(fg=SYN["control"]),
        "PreProc": dict(fg=SYN["preproc"]), "Include": dict(fg=SYN["preproc"]),
        "Type": dict(fg=SYN["type"]), "StorageClass": dict(fg=SYN["keyword"]),
        "Structure": dict(fg=SYN["type"]), "Special": dict(fg=SYN["escape"]),
        "Delimiter": dict(fg=P["muted"]), "Underlined": dict(fg=P["cyan"], underline=True),
        "Error": dict(fg=SYN["error"]), "Todo": dict(fg=P["bg"], bg=P["yellow"], bold=True),
        "DiffAdd": dict(bg="#1b3329"), "DiffChange": dict(bg="#2a2540"), "DiffDelete": dict(bg="#3a1f2a"),
        "DiffText": dict(bg="#3a3360"), "Added": dict(fg=P["green"]), "Changed": dict(fg=P["yellow"]),
        "Removed": dict(fg=P["pink"]),
        "DiagnosticError": dict(fg=P["pink"]), "DiagnosticWarn": dict(fg=P["yellow"]),
        "DiagnosticInfo": dict(fg=P["cyan"]), "DiagnosticHint": dict(fg=P["lilac"]),
        "DiagnosticUnderlineError": dict(undercurl=True, sp=P["pink"]),
        "DiagnosticUnderlineWarn": dict(undercurl=True, sp=P["yellow"]),
        "@variable": dict(fg=SYN["variable"]), "@variable.member": dict(fg=SYN["property"]),
        "@property": dict(fg=SYN["property"]), "@variable.builtin": dict(fg=SYN["builtin"], italic=True),
        "@function": dict(fg=SYN["function"]), "@function.builtin": dict(fg=SYN["builtin"]),
        "@function.method": dict(fg=SYN["function"]), "@constructor": dict(fg=SYN["type"]),
        "@keyword": dict(fg=SYN["keyword"]), "@keyword.return": dict(fg=SYN["control"], italic=True),
        "@type": dict(fg=SYN["type"]), "@type.builtin": dict(fg=SYN["type"], italic=True),
        "@string": dict(fg=SYN["string"]), "@string.escape": dict(fg=SYN["escape"]),
        "@number": dict(fg=SYN["number"]), "@boolean": dict(fg=SYN["constant"]),
        "@constant": dict(fg=SYN["constant"]), "@attribute": dict(fg=SYN["attribute"]),
        "@tag": dict(fg=SYN["tag"]), "@tag.attribute": dict(fg=SYN["property"]),
        "@punctuation": dict(fg=P["muted"]), "@operator": dict(fg=SYN["operator"]),
        "@comment": dict(fg=SYN["comment"], italic=True), "@markup.heading": dict(fg=P["accent"], bold=True),
        "@markup.link": dict(fg=P["cyan"], underline=True), "@markup.raw": dict(fg=P["green"]),
    }

    def val(v):
        return "true" if v is True else f'"{v}"'
    lines = ["-- AxolOS · tema de Neovim (generado por tools/editores_axolos.py)",
             'vim.cmd("highlight clear")',
             'if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end',
             'vim.o.background = "dark"', 'vim.g.colors_name = "axolos"', "local hl = vim.api.nvim_set_hl"]
    for g, spec in hl.items():
        body = ", ".join(f"{k} = {val(v)}" for k, v in spec.items())
        lines.append(f'hl(0, "{g}", {{ {body} }})')
    term = [P["bg_dark"], P["pink"], P["green"], P["yellow"], P["indigo"], P["accent"], P["cyan"], "#c9c9d3",
            P["faint"], P["pink_hi"], "#a8efcf", P["yellow_hi"], P["lilac"], P["accent_hi"], "#a9e6f1", P["white"]]
    lines += [f'vim.g.terminal_color_{i} = "{c}"' for i, c in enumerate(term)]
    return "\n".join(lines) + "\n"


# --- VS Code -----------------------------------------------------------------
def vscode_theme():
    a = lambda c, alpha: c + alpha  # noqa: E731  color hex + alfa hex
    colors = {
        "focusBorder": a(P["accent"], "80"), "foreground": P["fg"], "descriptionForeground": P["muted"],
        "errorForeground": P["pink"], "icon.foreground": P["muted"], "selection.background": a(P["accent"], "40"),
        "widget.border": P["border"], "widget.shadow": "#00000066",
        "button.background": P["accent_lo"], "button.foreground": P["white"], "button.hoverBackground": P["indigo"],
        "button.secondaryBackground": P["surface"], "button.secondaryForeground": P["fg"],
        "badge.background": P["accent"], "badge.foreground": P["bg_dark"],
        "activityBar.background": P["bg_dark"], "activityBar.foreground": P["fg"],
        "activityBar.inactiveForeground": P["faint"], "activityBar.activeBorder": P["accent"],
        "activityBarBadge.background": P["accent"], "activityBarBadge.foreground": P["bg_dark"],
        "activityBar.border": P["bg_dark"],
        "sideBar.background": P["bg_side"], "sideBar.foreground": P["fg"], "sideBar.border": P["bg_dark"],
        "sideBarTitle.foreground": P["muted"], "sideBarSectionHeader.background": P["bg_side"],
        "sideBarSectionHeader.border": P["border"],
        "titleBar.activeBackground": P["bg_dark"], "titleBar.activeForeground": P["fg"],
        "titleBar.inactiveBackground": P["bg_dark"], "titleBar.inactiveForeground": P["muted"],
        "titleBar.border": P["bg_dark"],
        "statusBar.background": P["bg_dark"], "statusBar.foreground": P["muted"], "statusBar.border": P["bg_dark"],
        "statusBar.debuggingBackground": P["accent_lo"], "statusBar.debuggingForeground": P["white"],
        "statusBar.noFolderBackground": P["bg_dark"], "statusBarItem.remoteBackground": P["accent_lo"],
        "statusBarItem.remoteForeground": P["white"], "statusBarItem.hoverBackground": "#ffffff12",
        "editorGroupHeader.tabsBackground": P["bg_side"], "editorGroupHeader.tabsBorder": P["bg_side"],
        "editorGroup.border": P["bg_dark"],
        "tab.activeBackground": P["bg"], "tab.activeForeground": P["white"], "tab.activeBorderTop": P["accent"],
        "tab.inactiveBackground": P["bg_side"], "tab.inactiveForeground": P["muted"], "tab.border": P["bg_side"],
        "tab.hoverBackground": P["bg"], "tab.unfocusedActiveBorderTop": P["faint"],
        "breadcrumb.foreground": P["muted"], "breadcrumb.focusForeground": P["fg"],
        "editor.background": P["bg"], "editor.foreground": P["fg"],
        "editorLineNumber.foreground": P["faint"], "editorLineNumber.activeForeground": P["accent_hi"],
        "editorCursor.foreground": P["accent"], "editor.selectionBackground": a(P["accent"], "40"),
        "editor.inactiveSelectionBackground": a(P["accent"], "22"),
        "editor.selectionHighlightBackground": a(P["accent"], "22"),
        "editor.wordHighlightBackground": a(P["accent"], "22"),
        "editor.findMatchBackground": a(P["yellow"], "55"), "editor.findMatchHighlightBackground": a(P["accent"], "33"),
        "editor.lineHighlightBackground": "#ffffff07", "editor.lineHighlightBorder": "#00000000",
        "editorIndentGuide.background1": P["border"], "editorIndentGuide.activeBackground1": P["faint"],
        "editorWhitespace.foreground": P["border"], "editorRuler.foreground": P["border"],
        "editorBracketMatch.background": a(P["accent"], "30"), "editorBracketMatch.border": a(P["accent"], "80"),
        "editorBracketHighlight.foreground1": P["accent"], "editorBracketHighlight.foreground2": P["cyan"],
        "editorBracketHighlight.foreground3": P["yellow"], "editorBracketHighlight.foreground4": P["green"],
        "editorBracketHighlight.foreground5": P["pink_hi"], "editorBracketHighlight.foreground6": P["lilac"],
        "editorError.foreground": P["pink"], "editorWarning.foreground": P["yellow"], "editorInfo.foreground": P["cyan"],
        "editorGutter.addedBackground": P["green"], "editorGutter.modifiedBackground": P["yellow"],
        "editorGutter.deletedBackground": P["pink"],
        "editorWidget.background": P["surface"], "editorWidget.border": P["border"],
        "editorSuggestWidget.background": P["surface"], "editorSuggestWidget.selectedBackground": a(P["accent"], "33"),
        "editorSuggestWidget.highlightForeground": P["accent_hi"], "editorHoverWidget.background": P["surface"],
        "editorHoverWidget.border": P["border"], "editorOverviewRuler.border": P["bg"],
        "minimap.background": P["bg"], "scrollbarSlider.background": "#ffffff14",
        "scrollbarSlider.hoverBackground": "#ffffff22", "scrollbarSlider.activeBackground": a(P["accent"], "55"),
        "input.background": P["bg_dark"], "input.border": P["border"], "input.foreground": P["fg"],
        "input.placeholderForeground": P["faint"], "inputOption.activeBorder": P["accent"],
        "dropdown.background": P["surface"], "dropdown.border": P["border"],
        "list.activeSelectionBackground": a(P["accent"], "33"), "list.activeSelectionForeground": P["white"],
        "list.inactiveSelectionBackground": "#ffffff0f", "list.hoverBackground": "#ffffff0a",
        "list.focusOutline": a(P["accent"], "80"), "list.highlightForeground": P["accent_hi"],
        "tree.indentGuidesStroke": P["border"],
        "panel.background": P["bg_side"], "panel.border": P["border"],
        "panelTitle.activeBorder": P["accent"], "panelTitle.activeForeground": P["fg"],
        "panelTitle.inactiveForeground": P["muted"],
        "terminal.background": P["bg_side"], "terminal.foreground": P["fg"], "terminalCursor.foreground": P["accent"],
        "terminal.ansiBlack": P["bg_dark"], "terminal.ansiRed": P["pink"], "terminal.ansiGreen": P["green"],
        "terminal.ansiYellow": P["yellow"], "terminal.ansiBlue": P["indigo"], "terminal.ansiMagenta": P["accent"],
        "terminal.ansiCyan": P["cyan"], "terminal.ansiWhite": "#c9c9d3", "terminal.ansiBrightBlack": P["faint"],
        "terminal.ansiBrightRed": P["pink_hi"], "terminal.ansiBrightGreen": "#a8efcf",
        "terminal.ansiBrightYellow": P["yellow_hi"], "terminal.ansiBrightBlue": P["lilac"],
        "terminal.ansiBrightMagenta": P["accent_hi"], "terminal.ansiBrightCyan": "#a9e6f1",
        "terminal.ansiBrightWhite": P["white"],
        "gitDecoration.addedResourceForeground": P["green"], "gitDecoration.modifiedResourceForeground": P["yellow"],
        "gitDecoration.deletedResourceForeground": P["pink"], "gitDecoration.untrackedResourceForeground": P["green"],
        "gitDecoration.ignoredResourceForeground": P["faint"], "gitDecoration.conflictingResourceForeground": P["accent"],
        "diffEditor.insertedTextBackground": "#7ddfb422", "diffEditor.removedTextBackground": "#ff7a9322",
        "peekView.border": P["accent_lo"], "peekViewEditor.background": P["bg_side"],
        "peekViewResult.background": P["surface"], "peekViewTitle.background": P["surface"],
        "notifications.background": P["surface"], "notifications.border": P["border"],
        "quickInput.background": P["surface"], "quickInputList.focusBackground": a(P["accent"], "33"),
        "menu.background": P["surface"], "menu.selectionBackground": a(P["accent"], "33"),
        "menu.border": P["border"], "textLink.foreground": P["accent_hi"], "textLink.activeForeground": P["accent"],
        "progressBar.background": P["accent"], "editorLink.activeForeground": P["cyan"],
        "welcomePage.tileBackground": P["surface"], "walkThrough.embeddedEditorBackground": P["bg_side"],
    }

    def tok(scope, color, style=None):
        s = {"foreground": color}
        if style:
            s["fontStyle"] = style
        return {"scope": scope, "settings": s}
    tokens = [
        tok(["comment", "punctuation.definition.comment"], SYN["comment"], "italic"),
        tok(["string", "string.quoted", "markup.inline.raw"], SYN["string"]),
        tok(["constant.character.escape", "string.regexp", "constant.other.placeholder"], SYN["escape"]),
        tok(["constant.numeric", "constant.language", "constant.other", "support.constant"], SYN["number"]),
        tok(["keyword", "storage", "storage.type", "storage.modifier"], SYN["keyword"]),
        tok(["keyword.control", "keyword.control.flow", "keyword.control.return"], SYN["control"]),
        tok(["keyword.operator", "punctuation.accessor"], SYN["operator"]),
        tok(["keyword.control.import", "keyword.control.directive", "meta.preprocessor"], SYN["preproc"]),
        tok(["entity.name.function", "support.function", "meta.function-call"], SYN["function"]),
        tok(["entity.name.type", "entity.name.class", "support.type", "support.class",
             "entity.other.inherited-class", "storage.type.class"], SYN["type"]),
        tok(["variable", "meta.definition.variable"], SYN["variable"]),
        tok(["variable.other.property", "variable.other.object.property", "meta.object-literal.key",
             "support.type.property-name", "entity.other.attribute-name"], SYN["property"]),
        tok(["variable.language", "support.variable"], SYN["builtin"], "italic"),
        tok(["variable.parameter"], P["accent_hi"], "italic"),
        tok(["entity.name.tag"], SYN["tag"]),
        tok(["meta.decorator", "entity.name.function.decorator", "punctuation.decorator"], SYN["attribute"]),
        tok(["punctuation", "meta.brace"], P["muted"]),
        tok(["markup.heading", "entity.name.section"], P["accent"], "bold"),
        tok(["markup.bold"], P["accent_hi"], "bold"), tok(["markup.italic"], P["fg"], "italic"),
        tok(["markup.underline.link", "string.other.link"], P["cyan"]),
        tok(["markup.inserted"], P["green"]), tok(["markup.deleted"], P["pink"]),
        tok(["markup.changed"], P["yellow"]), tok(["invalid"], P["pink"], "underline"),
    ]
    semantic = {"parameter": {"foreground": P["accent_hi"], "italic": True},
                "property": P["accent_hi"], "enumMember": SYN["constant"], "namespace": SYN["type"],
                "*.defaultLibrary": {"foreground": SYN["builtin"]}}
    return {"name": "AxolOS", "type": "dark", "semanticHighlighting": True,
            "colors": colors, "tokenColors": tokens, "semanticTokenColors": semantic}


def vscode_vsix(out: Path):
    pkg = {
        "name": "axolos-theme", "displayName": "AxolOS", "description": "Tema oficial de AxolOS",
        "version": VERSION, "publisher": "axolos", "license": "MIT",
        "engines": {"vscode": "^1.70.0"}, "categories": ["Themes"],
        "contributes": {"themes": [{"label": "AxolOS", "uiTheme": "vs-dark",
                                    "path": "./themes/axolos-color-theme.json"}]},
    }
    manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="axolos-theme" Version="{VERSION}" Publisher="axolos" />
    <DisplayName>AxolOS</DisplayName>
    <Description xml:space="preserve">Tema oficial de AxolOS</Description>
    <Categories>Themes</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.70.0" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui,workspace" />
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""
    ctypes = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension=".json" ContentType="application/json"/><Default Extension=".vsixmanifest" ContentType="text/xml"/></Types>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("extension.vsixmanifest", manifest)
        z.writestr("extension/package.json", json.dumps(pkg, indent=2))
        z.writestr("extension/themes/axolos-color-theme.json", json.dumps(vscode_theme(), indent=2))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    d = Path(sys.argv[1])
    (d / "kate").mkdir(parents=True, exist_ok=True)
    (d / "nvim").mkdir(parents=True, exist_ok=True)
    (d / "kate/axolos.theme").write_text(kate(), encoding="utf-8")
    (d / "nvim/axolos.lua").write_text(nvim(), encoding="utf-8")
    vscode_vsix(d / "vscode/axolos-theme.vsix")
    print("Temas generados en", d)


if __name__ == "__main__":
    main()
