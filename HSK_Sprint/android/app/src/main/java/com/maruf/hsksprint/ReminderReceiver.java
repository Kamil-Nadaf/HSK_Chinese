package com.maruf.hsksprint;
import android.app.*;
import android.content.*;
import android.os.Build;
import java.util.Calendar;
public class ReminderReceiver extends BroadcastReceiver {
  static final String CH = "reminders";
  @Override public void onReceive(Context c, Intent i) {
    SharedPreferences p = c.getSharedPreferences("rem", Context.MODE_PRIVATE);
    if (!p.getBoolean("on", false)) return;
    if (!Intent.ACTION_BOOT_COMPLETED.equals(i.getAction())) show(c, p.getString("title", "HSK Sprint"), p.getString("body", "Time to practise."));
    schedule(c);
  }
  static void show(Context c, String title, String body) {
    NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
    if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(new NotificationChannel(CH, "Study reminders", NotificationManager.IMPORTANCE_DEFAULT));
    PendingIntent pi = PendingIntent.getActivity(c, 0, new Intent(c, MainActivity.class), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, CH) : new Notification.Builder(c);
    b.setSmallIcon(android.R.drawable.ic_popup_reminder).setContentTitle(title).setContentText(body).setStyle(new Notification.BigTextStyle().bigText(body)).setContentIntent(pi).setAutoCancel(true);
    nm.notify(1, b.build());
  }
  static PendingIntent pi(Context c) {
    return PendingIntent.getBroadcast(c, 7, new Intent(c, ReminderReceiver.class), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
  }
  static void schedule(Context c) {
    SharedPreferences p = c.getSharedPreferences("rem", Context.MODE_PRIVATE);
    AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
    am.cancel(pi(c));
    if (!p.getBoolean("on", false)) return;
    Calendar t = Calendar.getInstance();
    t.set(Calendar.HOUR_OF_DAY, p.getInt("h", 20)); t.set(Calendar.MINUTE, p.getInt("m", 0)); t.set(Calendar.SECOND, 0); t.set(Calendar.MILLISECOND, 0);
    if (t.getTimeInMillis() <= System.currentTimeMillis() + 5000) t.add(Calendar.DAY_OF_YEAR, 1);
    am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t.getTimeInMillis(), pi(c));
  }
}
