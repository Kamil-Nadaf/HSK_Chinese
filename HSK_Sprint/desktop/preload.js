const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('hskNative', {
  platform: 'desktop',
  setReminder: (on, h, m, title, body) => ipcRenderer.send('rem:set', { on: !!on, h: +h, m: +m, title: String(title), body: String(body) }),
  testNotification: (title, body) => ipcRenderer.send('rem:test', { title: String(title), body: String(body) })
});
