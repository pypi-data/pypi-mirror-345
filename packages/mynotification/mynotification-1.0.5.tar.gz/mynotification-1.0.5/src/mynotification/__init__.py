class Notification:
    def __init__(self, title: str, message: str, platform: str = "linux"):
        self.title = title
        self.message = message
        self.platform = platform.lower()
        print(
            f"Notification initialized with title='{self.title}', message='{self.message}', platform='{self.platform}'"
        )

    def send_mynotification(self):
        desktop = ["linux", "windows", "macos"]
        print(f"send_mynotification called. Platform: {self.platform}")
        if self.platform == "android":
            print("Using Android notification handler.")
            from mynotification.notification_android import send_notification

            send_notification(title=self.title, message=self.message)
        elif self.platform in desktop:
            print("Using desktop notification handler.")
            from mynotification.notification_desktop import send_notification

            send_notification(title=self.title, message=self.message)
        else:
            print(f"Unsupported platform: {self.platform}")
