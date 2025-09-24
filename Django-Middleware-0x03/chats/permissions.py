from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of a conversation to access messages.
    Restrict PUT, PATCH, DELETE to participants only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
        elif hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            is_participant = request.user in obj.conversation.participants.all()
        else:
            is_participant = False
    
        if request.method in ["PUT","PATCH", "DELETE"]:
            return is_participant
        
        return is_participant
        