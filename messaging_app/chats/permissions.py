from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to participants of conversation.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return user in obj.conversation.participants.all()
        return False
        