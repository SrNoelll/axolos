# Security

## Signing key

Every AxolOS package and the repository database are signed with this OpenPGP key:

```
AxolOS (firma de paquetes) <159236885+SrNoelll@users.noreply.github.com>
3F7D A47A 1271 EB49 F17F  573F 992D B143 AB09 9E91
```

The public key is [`axolos.gpg`](axolos.gpg) and ships in the `axolos-keyring` package.
`install.sh` refuses to continue if the fingerprint does not match. pacman checks every signature.

## Reporting a vulnerability

Please **do not open a public issue**. Use GitHub's private reporting:
[Security → Report a vulnerability](https://github.com/SrNoelll/axolos/security/advisories/new).
You can write in English, Español, Français, Русский, 中文 or 日本語.

Things worth reporting: anything that lets a package or script run code it should not, the
`axolos-root` helper (pkexec) accepting unexpected input, or the publication workflow trusting
something it should not.

## Supported versions

Only the packages currently published in the [`x86_64`](https://github.com/SrNoelll/axolos/releases/tag/x86_64)
release are supported; `sudo pacman -Syu` always brings the latest ones.
