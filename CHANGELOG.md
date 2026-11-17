# Changelog

AxolOS packages are published continuously; each entry groups a visible change.

## 2026-11-17 — Liquid glass everywhere

- The glass effect now really turns on: the safety hook misread CachyOS package versions
  (`6.12.0-5.1`) and kept the effect paused even with the right KWin.
- Glass tuned like Apple's Liquid Glass: clear center with light blur, refraction concentrated on
  the edge, chromatic fringing, rim light and an adaptive tint that only thickens when what is
  behind would make text hard to read.
- Top bar, dock, menus (Bento and every popup), notifications, tooltips, terminal and window
  sidebars are glass in both modes: Plasma frames were using the near-opaque variant, the dock was
  set to opaque and new accounts started with old colors.
- Light mode uses its own purple (the dark one was kept by accounts and was hard to read on light glass)
  and its own icon theme variant, so toolbar icons are dark on light glass instead of white on white.
- Wallpapers, boot logo and screenshots re-rendered: the glass axolotl now has smooth, rounded edges
  (no pixel steps on its outline) and its rim catches color instead of a dark line.

## 2026-11-17 — Liquid glass

- Real liquid glass in KWin (`axolos-glass`, the Glass effect by 4v3ngR): refraction, chromatic edges
  and rim light on panels, menus and windows; rebuilt automatically for every new KWin, with a safety
  hook that falls back to normal blur when versions do not match.
- New look, dark (default) and light: 3D-rendered glass axolotl wallpapers, glass Plasma frames,
  colors, Kvantum, window decorations, Bento menu, login screen with real refraction in QML,
  glass icons, boot screen and installer.
- `axolos-aspecto` and AxolOS Center → Appearance: dark, light or automatic.
- The AxolOS apps follow the light or dark mode and become translucent with the glass effect.

## 2026-11-17 — Six languages

- AxolOS follows the system language: English, Español, Français, Русский, 简体中文 and 日本語
  (programs, Bento menu, login screen, launchers, installer and package descriptions).
- English aliases for commands and profiles (`axolos-ia download`, `axolos-dev install containers`).
- Fixes found while translating: `_` variables that broke model downloads, Open WebUI, exporting and
  attaching in Axo, Download in the Center and `axolos-navegadores`.
- Checks on every push: code, scripts, launchers and complete translations.

## 2026-11-08 — Signed repository and installer

- Packages published automatically by GitHub Actions to a signed pacman repository.
- AxolOS ISO with branded Calamares installer, online and offline install.
- AxolOS Center, per-app icons, local AI (Axo) with file search, developer profiles.
