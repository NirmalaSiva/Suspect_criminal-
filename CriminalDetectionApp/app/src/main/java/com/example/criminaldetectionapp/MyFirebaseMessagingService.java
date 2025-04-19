package com.example.criminaldetectionapp;

import android.annotation.SuppressLint;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

@SuppressLint("MissingFirebaseInstanceTokenRefresh")
public class MyFirebaseMessagingService extends FirebaseMessagingService {

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        Handler handler = new Handler(Looper.getMainLooper());
//        handler.post(() -> Toast.makeText(getApplicationContext(), "onMessageReceived", Toast.LENGTH_SHORT).show());
        Log.d("FCM", "From: " + remoteMessage.getFrom());
        Log.d("FCM", "Data Payload: " + remoteMessage.getData());
        if (remoteMessage.getNotification() != null) {
            Log.d("FCM", "Notification Body: " + remoteMessage.getNotification().getBody());
        }
        // Extract data from the message
        String name = remoteMessage.getData().get("name");
        String date = remoteMessage.getData().get("date");
        String time = remoteMessage.getData().get("time");
        String imageUrl = remoteMessage.getData().get("image");

        String title = "Criminal Detected!";
        String message = "Name: " + name + "\nDate: " + date + "\nTime: " + time;

        // Call the method to show notification
        sendNotification(title, message, name, date, time, imageUrl);
    }

    private void sendNotification(String title, String message, String name, String date, String time, String imageUrl) {
        Intent intent = new Intent(this, DetailActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

        intent.putExtra("name", name);
        intent.putExtra("date", date);
        intent.putExtra("time", time);
        intent.putExtra("image_url", imageUrl);

        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, intent, PendingIntent.FLAG_ONE_SHOT | PendingIntent.FLAG_IMMUTABLE);

        String channelId = "CriminalAlert";
        Uri defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        NotificationCompat.Builder notificationBuilder =
                new NotificationCompat.Builder(this, channelId)
                        .setSmallIcon(R.mipmap.ic_launcher)
                        .setContentTitle(title)
                        .setContentText("Tap to view details")
                        .setStyle(new NotificationCompat.BigTextStyle().bigText(message))
                        .setAutoCancel(true)
                        .setSound(defaultSoundUri)
                        .setContentIntent(pendingIntent)
                        .setPriority(NotificationCompat.PRIORITY_HIGH);

        NotificationManager notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId, "Criminal Alerts", NotificationManager.IMPORTANCE_HIGH);
            notificationManager.createNotificationChannel(channel);
        }

        notificationManager.notify(101, notificationBuilder.build());
    }

}
