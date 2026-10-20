package com.maruf.hsksprint;
import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.*;
public class MainActivity extends Activity {
  WebView w;
  ValueCallback<Uri[]> fileCb;
  static final int FILE = 11;
  class Bridge {
    @JavascriptInterface public String platform() { return "android"; }
    @JavascriptInterface public void setReminder(boolean on, int h, int m, String title, String body) {
      getSharedPreferences("rem", MODE_PRIVATE).edit().putBoolean("on", on).putInt("h", h).putInt("m", m).putString("title", title).putString("body", body).apply();
      if (on) askPermission();
      ReminderReceiver.schedule(MainActivity.this);
    }
    @JavascriptInterface public void testNotification(String title, String body) {
      askPermission();
      ReminderReceiver.show(MainActivity.this, title, body);
    }
  }
  void askPermission() {
    if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED)
      runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 5));
  }
  @Override protected void onCreate(Bundle b) {
    super.onCreate(b);
    getWindow().setStatusBarColor(Color.parseColor("#0F5B63"));
    w = new WebView(this); setContentView(w);
    WebSettings s = w.getSettings();
    s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true);
    s.setAllowFileAccess(true); s.setMediaPlaybackRequiresUserGesture(false);
    w.addJavascriptInterface(new Bridge(), "HSKNative");
    w.setWebViewClient(new WebViewClient());
    w.setWebChromeClient(new WebChromeClient() {
      @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
        if (fileCb != null) fileCb.onReceiveValue(null);
        fileCb = cb;
        try { startActivityForResult(p.createIntent(), FILE); } catch (Exception e) { fileCb = null; return false; }
        return true;
      }
    });
    if (b != null) w.restoreState(b); else w.loadUrl("file:///android_asset/site/index.html");
  }
  @Override protected void onActivityResult(int req, int res, Intent d) {
    if (req == FILE && fileCb != null) { fileCb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, d)); fileCb = null; }
    else super.onActivityResult(req, res, d);
  }
  @Override protected void onSaveInstanceState(Bundle o) { super.onSaveInstanceState(o); w.saveState(o); }
  @Override public void onBackPressed() { if (w.canGoBack()) w.goBack(); else super.onBackPressed(); }
}
