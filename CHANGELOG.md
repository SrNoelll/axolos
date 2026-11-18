# Changelog

AxolOS packages are published continuously; each entry groups a visible change.

## 2026-11-18 — Login fix

- `axolos-glass` 1.6.4-4 could crash KWin (and the login screen) on processors without AVX-512: the
  build used the build server's processor (`-march=native`). It is now built for any x86-64 processor,
  the build fails if the effect contains AVX/AVX-512 instructions, and the pacman hook sets the effect
  aside (normal blur) if it ever needs instructions the processor lacks.
- The login screen never loads the KWin glass effect (its refraction is drawn in QML), so a broken
  effect can no longer prevent logging in.

## 2026-11-18 — Windows and global themes

- Applying the AxolOS global theme with “Desktop and window layout” now sets up the AxolOS desktop (top
  bar, glass dock with Bento, clock) instead of KDE's default panel.
- Window title bars redrawn: the same glass as the window in both focused and unfocused windows (the
  focused one turned solid grey), no outline, 14 px corners and a soft shadow that follows them.
- Windows no longer get a light rim on their edge (menus, panels and notifications keep it).
- The Bento icon in the dock follows the light or dark text color.
- GTK apps (Files and other libadwaita apps, GTK3) and the AxolOS apps are glass like the terminal, in
  both modes; Dolphin's file view too.
- Panel, menu and notification shadows follow the rounded corners (there was a square around them).
- Glass icons also for Files (Nautilus), GNOME Terminal/Console and GNOME Settings.
- `axolos-aspecto` and `axolos-navegadores` were installed without execute permission, so the update
  of existing accounts at login never ran.

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
