from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Message

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    user = request.user
    user.delete()
    return JsonResponse({'message': 'User account and related data deleted successfully.'})

@login_required
def unread_inbox(request):
    unread_messages = Message.unread.unread_for_user(request.user)
    data = [
        {
            'id': msg.id,
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp
        }
        for msg in unread_messages
    ]
    return JsonResponse({'unread_messages': data})




