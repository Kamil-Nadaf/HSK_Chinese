const { app, BrowserWindow, Notification, Tray, Menu, ipcMain, nativeImage, shell } = require('electron');
const path = require('path');
const fs = require('fs');

let win = null, tray = null, quitting = false;
const iconPath = path.join(__dirname, 'build', 'icon.png');
const cfgFile = () => path.join(app.getPath('userData'), 'reminder.json');
let rem = { on: false, h: 20, m: 0, title: 'HSK Sprint', body: 'Time to practise.', last: '' };
try { rem = Object.assign(rem, JSON.parse(fs.readFileSync(cfgFile(), 'utf8'))); } catch (e) {}
const saveRem = () => { try { fs.writeFileSync(cfgFile(), JSON.stringify(rem)); } catch (e) {} };
const today = () => { const d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); };

if (!app.requestSingleInstanceLock()) { app.quit(); }
else app.on('second-instance', () => showWin());

function showWin() {
  if (!win) createWin(false);
  if (win.isMinimized()) win.restore();
  win.show(); win.focus();
}

function createWin(hidden) {
  win = new BrowserWindow({
    width: 480, height: 860, minWidth: 360, minHeight: 560, title: 'HSK Sprint',
    show: !hidden, backgroundColor: '#E8F0EA', icon: iconPath,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, 'site', 'index.html'));
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.on('close', (e) => { if (!quitting && rem.on) { e.preventDefault(); win.hide(); } });
  win.on('closed', () => { win = null; });
}

function notify(title, body) {
  if (!Notification.isSupported()) return;
  const n = new Notification({ title, body, icon: iconPath });
  n.on('click', showWin);
  n.show();
}

function applyLogin() {
  try { app.setLoginItemSettings({ openAtLogin: !!rem.on, args: ['--hidden'] }); } catch (e) {}
}

function tick() {
  if (!rem.on) return;
  const d = new Date();
  const due = d.getHours() * 60 + d.getMinutes() >= rem.h * 60 + rem.m;
  if (due && rem.last !== today()) { rem.last = today(); saveRem(); notify(rem.title, rem.body); }
}

ipcMain.on('rem:set', (e, r) => {
  const was = rem.on;
  if (r.h >= 0 && r.h < 24 && r.m >= 0 && r.m < 60) { rem.h = r.h; rem.m = r.m; }
  rem.on = !!r.on; rem.title = r.title.slice(0, 80); rem.body = r.body.slice(0, 300);
  // Turning it on after the set time today should not fire at once; wait for tomorrow.
  if (rem.on && !was) { const d = new Date(); if (d.getHours() * 60 + d.getMinutes() >= rem.h * 60 + rem.m) rem.last = today(); }
  saveRem(); applyLogin();
});
ipcMain.on('rem:test', (e, r) => notify(r.title.slice(0, 80), r.body.slice(0, 300)));

app.whenReady().then(() => {
  createWin(process.argv.includes('--hidden') && rem.on);
  try {
    const img = nativeImage.createFromPath(iconPath).resize({ width: 18, height: 18 });
    tray = new Tray(img);
    tray.setToolTip('HSK Sprint');
    tray.setContextMenu(Menu.buildFromTemplate([
      { label: 'Open HSK Sprint', click: showWin },
      { label: 'Quit', click: () => { quitting = true; app.quit(); } }
    ]));
    tray.on('click', showWin);
  } catch (e) {}
  setInterval(tick, 20000);
  app.on('activate', showWin);
});
app.on('before-quit', () => { quitting = true; });
app.on('window-all-closed', () => { if (!rem.on) app.quit(); });
