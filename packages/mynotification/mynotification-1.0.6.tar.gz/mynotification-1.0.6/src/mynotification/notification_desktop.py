from notifypy import Notify


def send_notification(title: str, message: str):
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.send()
