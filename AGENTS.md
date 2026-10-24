# AGENTS.md

Instructions for coding agents (Antigravity, Gemini CLI, Claude Code, Codex, Cursor, Copilot and others) working in
this repository. People should start with [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md);
this file repeats their rules in the form an agent needs, and links to them for the detail.

Repository: **https://github.com/bio-colab/MyTv**

## First: which job are you doing?

| You were asked to | Do this |
|---|---|
| Clean up a TV: debloat it, assess hardware, install the launcher, push a theme | Read [`skills/mytv/SKILL.md`](skills/mytv/SKILL.md) and [`PROMPT.md`](PROMPT.md) and follow them on the real TV. Run `tools/assess_device.py <tv_ip>` first to detect device tier and regional apps. Use the tools in `tools/` and the launcher in `launcher/` rather than writing new ones; the only file you need to change is `launcher/app/src/main/res/values/config.xml`, or a theme's `config.json`, for this TV. Do not edit the repo's docs, tests or other code, and do not open issues or pull requests unless the person asks you to. |
| Change this repo: a TV list, a fix, a translation, a theme, docs | Skip the next section and read on from [Repo map](#repo-map). |

### Cleaning a TV: the rules that are not negotiable

[`skills/mytv/SKILL.md`](skills/mytv/SKILL.md) and [`PROMPT.md`](PROMPT.md) contain the procedure. Safety rules in brief:

- **Assess hardware first**: Run `python tools/assess_device.py <tv_ip>`. For Tier 1 devices (RAM <= 1GB, low storage, or budget CVTE/MStar boards), strictly apply the `ultra-lite` profile.
- **Protect regional Arab streaming apps**: Never disable Shahid (`com.mbc.shahid`), TOD (`com.tod`), beIN, Watch IT, Starzplay, Quran apps, or IPTV apps.
- **Protect third-party app stores on AOSP TVs**: Many budget TVs lack Google Play Store; never disable stores like Aptoide or APKPure.
- **Disable, never uninstall**: `pm disable-user --user 0`, one package per shell call. No `pm uninstall`, no root, nothing flashed. Every step must be undone by `tools/restore.sh` / `tools/restore.ps1` or `tools/disable.sh`.
- **Back up first**: Package list, disabled list, `getprop` and settings into `backup/` before the first change.
- **Leave alone what the TV needs to work**: The TV app and input services behind HDMI and the tuner, the input/source menu, remote and Bluetooth pairing, on-screen keyboard, Play Store and Play Services.
- **Never disable Android's core packages**: The permission controller, package installer, ext services/shared and module metadata, `com.android.systemui`, `com.android.shell`, `com.android.settings`, `android`.
- **Never start a factory or test package** (`com.cvte.tv.hkcfac`, `mediatek.factorymenu.ui` and the like).
- **Keep the Home guard**: The stock launcher is disabled only after the new launcher is installed and confirmed as Home. On CVTE boards, leave stock launcher enabled until new launcher and input sources are thoroughly verified.
- **Ask before touching user apps**: Ask the person which apps they use with a checklist question.
- **Disable in small batches** and screenshot between them (`tools/tv.py --screenshot shots/01.png`).
- **Close ADB afterwards**: USB debugging and Network debugging off, authorisations revoked, reboot, and check `tools/adb-closed.py <tv ip>`.

The person's backups (`backup/`), screenshots (`shots/`), notes (`work/`) and the ADB key (`tools/adbkey/`) are listed in `.gitignore` and must never be committed.

## Repo map

| Path | What it is |
|---|---|
| `skills/mytv/SKILL.md` | The comprehensive Antigravity agent skill with hardware assessment and safe runbooks. |
| `PROMPT.md` | The prompt people paste into their agent. Brand-neutral; safety rules live here. |
| `README.md` | Arabic-first front page, explaining MyTv, hardware tiers, safety, and quick start. `README.en.md` is the English version. |
| `CONTRIBUTING.md` | The contributor guide for people. |
| `SECURITY.md` | Private vulnerability reporting. |
| `SHOWCASE.md` | Projects built on this repo that live in their own repositories. |
| `examples/README.md` | Tested TV model profiles index; holds rows for each `debloat.txt` and `tv.json`. |
| `launcher/` | The reference launcher: plain Java, AndroidX RecyclerView and DynamicAnimation, `minSdk` 26, no `INTERNET` permission. |
| `themes/` | Theme folders: `config.json`, `screenshot.jpg`. Includes `themes/ultra-lite/`. |
| `addons/` | Optional module-card apps, each its own Gradle project, never built into the launcher. |
| `tools/` | The ADB client (`tv.py`), hardware assessor (`assess_device.py`), `tools/disable.sh`, and helper scripts. |
| `tests/` | Python `unittest` suite. |
| `.github/maintainer/MAINTAINER.md` | Procedures for repo maintainers. |

## Where a change goes

| The change | Where it goes |
|---|---|
| A TV list: debloat list, notes, `tv.json` | [`docs/workflows/tv-list.md`](docs/workflows/tv-list.md) |
| A bug fix, doc note, or edge case | [`docs/workflows/docs-notes.md`](docs/workflows/docs-notes.md) |
| A new launcher translation or fix | [`docs/workflows/translation.md`](docs/workflows/translation.md) |
| A small launcher switch that is off by default | [`docs/workflows/launcher-switch.md`](docs/workflows/launcher-switch.md) |
| A new look: colours, wallpaper, dock, columns | [`docs/workflows/theme.md`](docs/workflows/theme.md) (`themes/<name>/`) |
| A widget or tile module card | [`docs/workflows/addon.md`](docs/workflows/addon.md) (`addons/<name>/`) |
| Performance A/B benchmark | [`docs/workflows/perf-ab.md`](docs/workflows/perf-ab.md) |
| A whole new launcher or heavy rewrite | [`docs/workflows/showcase.md`](docs/workflows/showcase.md) (`SHOWCASE.md`) |

## Before opening a PR

- Tests: `python3 -m unittest discover -s tests -v` (under `CLEANYOURTV_STRICT`).
- Launcher: JDK 17, Android SDK 34 (`minSdk` 26). In `launcher/`: `./gradlew --no-daemon testReleaseUnitTest lintRelease assembleRelease`.
- APK size gate: APK must stay under 524,288 B (512 KB).
- Screenshots: Every visual change has a screenshot from a real TV in the PR description.
- Security: Report vulnerabilities privately per `SECURITY.md`.

## Where to ask

Discussions and issues go to: [https://github.com/bio-colab/MyTv/issues](https://github.com/bio-colab/MyTv/issues).
