# HSK Practice Sheet

Active-recall practice for HSK 1: spaced-repetition cards, quizzes, typing, stroke-order writing, sentence building and a mock exam based on the sample paper. Built around the class lectures (Lecture 1 to 12), and you can add new lecture words as the course goes on.

Developed by Kamil Nadaf. MIT licence (see the repo `LICENSE`).

## Install

Go to the **Releases** page of this repository (right-hand side of the repo home page, or the "Releases" link under About) and open the newest version. Under **Assets**, download the file for your device. Then follow the steps below. Nothing else needs to be installed.

Your progress is saved on each device separately. Use Settings, Copy backup to move it between devices.

### Android phone or tablet

1. On the phone, open the Releases page and download the file ending in `-android.apk`.
2. Open the downloaded file (from the notification, or from the Downloads app).
3. If Android says it can't install apps from this source, tap **Settings**, switch on **Allow from this source**, then go back.
4. Tap **Install**, then **Open**.
5. If Play Protect shows a warning, tap **More details**, then **Install anyway**. The app is not on the Play Store.
6. To get daily reminders, allow notifications when asked.

To update, install a newer APK over the old one. Your progress is kept.

### Mac

1. Download the `.dmg`: `...-mac-arm64.dmg` for Apple Silicon (M1, M2, M3, M4), `...-mac-x64.dmg` for Intel. Not sure? Apple menu, **About This Mac**: "Chip: Apple M..." means arm64, "Processor: Intel" means x64.
2. Double-click the `.dmg`. A window opens.
3. Drag **HSK Practice Sheet** onto the **Applications** folder.
4. Open **Applications**, **right-click** HSK Practice Sheet and choose **Open**, then click **Open** again. (The app is not notarised by Apple, so a normal double-click is blocked the first time. After this it opens normally.)
5. If macOS still refuses: System Settings, **Privacy & Security**, scroll down and click **Open Anyway** next to HSK Practice Sheet.

### Windows

1. Download the `...-win-x64.exe` installer.
2. Double-click it.
3. If a blue "Windows protected your PC" box appears, click **More info**, then **Run anyway**. (The installer is not signed with a paid certificate.)
4. Choose an install folder or keep the default, click **Install**, then **Finish**.
5. Open **HSK Practice Sheet** from the Start menu or the desktop shortcut.

### Linux

Choose one:

- **AppImage** (works on most distributions): download the file ending in `.AppImage`, then in a terminal run
  ```
  chmod +x HSK-Practice-Sheet-*.AppImage
  ./HSK-Practice-Sheet-*.AppImage
  ```
  Or right-click the file, Properties, Permissions, tick **Allow executing as a program**, and double-click it. If it won't start on Ubuntu 22.04 or newer, install FUSE: `sudo apt install libfuse2`.
- **Debian, Ubuntu, Mint** (`.deb`): download the file ending in `.deb`, then run
  ```
  sudo apt install ./HSK-Practice-Sheet-*.deb
  ```
  and start **HSK Practice Sheet** from the app menu.

### iPhone and iPad

There is no App Store version, because Apple only allows installs through a paid developer account. Use the web app instead:

1. Open **Safari** (it must be Safari) and go to `https://kamil-nadaf.github.io/HSK_Chinese/`.
2. Tap the **Share** button (square with an arrow).
3. Scroll down and tap **Add to Home Screen**, then **Add**.
4. Open it from the new icon on the Home Screen. It runs full screen and works offline after the first visit.

Daily reminders are not supported on iPhone and iPad. Use the Reminders app if you want a nudge.

### In any browser

Open `https://kamil-nadaf.github.io/HSK_Chinese/` on a phone or computer. In Chrome or Edge you can click the install icon in the address bar to install it as an app. After the first visit it also works offline.

### On a server (Docker)

`docker compose up -d --build` in the `HSK_Sprint` folder, then open `http://server:8088`. Or pull `ghcr.io/<owner>/hsk-sprint:latest`.

---

## Add words from new lectures

Today screen, **+ Add new words**:

- Look a word up by Chinese, pinyin or English, pick the match and choose the lecture it belongs to.
- Or import a `.docx`, `.txt`, `.md` or `.csv` file. Lines like `咖啡 | ka1 fei1 | coffee`, a table, or just a list of words all work. Headings such as `Lecture 14`, `Lesson 14` or `第十四课` tag the words below them automatically. Old `.doc` files must be saved as `.docx` first.
- Pinyin and meanings come from the bundled CC-CEDICT dictionary (`site/dict.js`), so this works offline.

## Profile, theme, goal and reminders

Tap the 汉语 logo (or the seal at the top right) to open **Profile and settings**. It has your profile, theme, daily reminder, goal, study options, backup and About. The profile (name, email) is stored on the device only; there is no account.

- **Themes:** Auto, Light, Dark, Paper (black and white) and Glass. Light and Dark also take an accent colour (Jade, Indigo, Plum, Rose, Amber, Ink).
- **Goal:** tap the days-left pill on the Today screen to set what you are working towards, the date, and how many new words a day (or automatic).
- **Dictionary:** the Dict tab searches 汉字, pinyin or English and can add words to any lecture.
- **Reminders** are real notifications in the Android app and the desktop apps. In a plain browser they only fire while the page is open.

## Turn on GitHub Pages (once)

Repository Settings, Pages, Source: **GitHub Actions**. Then run "Publish web app (GitHub Pages)" from the Actions tab, or push a change to `HSK_Sprint/site`.

## Folders

- `site/` the built web app (`index.html`, `dict.js`, `audio/` with 1050 recorded clips)
- `android/` WebView wrapper (Gradle, debug-signed with the committed `debug.keystore` so updates install over older builds)
- `desktop/` Electron wrapper for macOS, Windows and Linux
- `src/` sources that generate `site/index.html`: `template.html`, `vocab.txt`, `sentences.txt`, `qa.txt`, `sample.json`, `build.py`, `fonts/` (IBM Plex Sans, SIL OFL) and `pwa/` (manifest, service worker, icons)

## GitHub Actions

`.github/workflows/build.yml` builds on demand (Actions tab, Run workflow), on pull requests and on tags:

- Pages: `pages.yml` publishes `HSK_Sprint/site` to GitHub Pages on every push to `main` that changes it
- Android APK
- macOS `.dmg`, Windows `.exe`, Linux `.AppImage` and `.deb`
- Docker image pushed to GitHub Container Registry (not on pull requests)
- On a tag like `v1.1.0` it also publishes a GitHub Release with the APK, `.dmg`, `.exe`, `.AppImage` and `.deb`

## Rebuilding `site/index.html`

```
cd src
npm install            # hanzi-writer and stroke data
python3 build.py out --audio
cp out/index.html out/manifest.webmanifest out/sw.js out/icon-*.png ../site/
```
`dict.js` is generated by `build_dict.py` from the CC-CEDICT export and the complete-hsk-vocabulary list (see `LICENSE` notes below). The audio clips come from `gen_audio.py` (gTTS).

## Credits

- Stroke order: Hanzi Writer (MIT) and hanzi-writer-data (Arphic Public License)
- Dictionary: CC-CEDICT, licensed CC BY-SA 4.0 (https://cc-cedict.org). `site/dict.js` stays under CC BY-SA 4.0.
- Interface font: IBM Plex Sans (SIL Open Font License 1.1); Chinese text uses Noto Serif SC or the system serif font
- Frequency order: drkameleon/complete-hsk-vocabulary
