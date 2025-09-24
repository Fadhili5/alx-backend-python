from django.contrib import admin
from .models import User, Conversation, ConversationParticipant, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'created_at', 'updated_at']
    list_filter = ['created_at']
    
@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'participant', 'joined_at', 'is_active']
    list_filter = ['joined_at', 'is_active']
    search_fields = ['participant__email', 'participant__first_name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'sent_at', 'is_read']
    list_filter = ['sent_at', 'is_read']
    search_fields = ['message_body']

