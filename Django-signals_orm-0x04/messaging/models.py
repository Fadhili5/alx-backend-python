from django.db import models
from django.contrib.auth import get_user_model
from .models import UnreadMessagesManager

User = get_user_model()

# class UnreadMessagesManager(models.Model):
#     def for_user(self, user):
#         return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'content', 'timestamp')

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    
    objects = models.Manager()
    unread = UnreadMessagesManager()

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"

    def get_thread(self):
        """
        Recursively fetch all replies to this message.
        """
        def fetch_replies(message):
            replies = list(message.replies.all().select_related('sender', 'receiver').prefetch_related('replies'))
            return [
                {
                    'id': reply.id,
                    'sender': reply.sender.username,
                    'receiver': reply.receiver.username,
                    'content': reply.content,
                    'timestamp': reply.timestamp,
                    'replies': fetch_replies(reply)
                }
                for reply in replies
            ]
        return fetch_replies(self)



class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for message {self.message.id} at {self.edited_at}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_histories')
    
    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"
    