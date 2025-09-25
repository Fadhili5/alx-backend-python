from django.contrib import admin
from .models import Message, Notification

class MessagingConfig(AppConfig):
    name = 'messaging'

    def ready(self):
        import messaging.signals