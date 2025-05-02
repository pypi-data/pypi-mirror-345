from jnius import autoclass
import os
import traceback


def send_notification(title: str, message: str):
    try:
        # Umgebungsvariable abrufen
        activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
        if not activity_host_class:
            raise ValueError(
                "Environment variable 'MAIN_ACTIVITY_HOST_CLASS_NAME' is not set."
            )

        # Java-Klassen laden
        activity_host = autoclass(activity_host_class)
        activity = activity_host.mActivity

        Context = autoclass("android.content.Context")
        NotificationManager = autoclass("android.app.NotificationManager")
        NotificationCompat = autoclass("androidx.core.app.NotificationCompat")
        NotificationChannel = autoclass("android.app.NotificationChannel")

        # Benachrichtigungs-Service abrufen
        notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
        channel_id = "my_notification_channel"
        channel_name = "My Notification Channel"
        channel_description = "Channel for app notifications"
        importance = NotificationManager.IMPORTANCE_DEFAULT

        # NotificationChannel erstellen (Android 8.0+)
        if int(activity.getApplicationInfo().targetSdkVersion) >= 26:
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription(channel_description)
            notification_service.createNotificationChannel(channel)

        # Benachrichtigung erstellen
        builder = NotificationCompat.Builder(activity, channel_id)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setSmallIcon(activity.getApplicationInfo().icon)
        builder.setAutoCancel(True)

        # Benachrichtigung senden
        notification_id = int(time.time())  # Dynamische ID basierend auf der Zeit
        notification = builder.build()
        notification_service.notify(notification_id, notification)

        print("Notification sent successfully.")

    except Exception as e:
        print("Error sending notification:", e)
        traceback.print_exc()
