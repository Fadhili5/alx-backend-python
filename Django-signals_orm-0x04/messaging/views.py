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
    unread_messages = Message.objects.filter(receiver=request.user, read=False).only('id', 'sender', 'content', 'timestamp').select_related('sender')
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




