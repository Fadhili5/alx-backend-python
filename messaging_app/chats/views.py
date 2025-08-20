from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .permissions import IsParticipantOfConversation
from .models import User, Conversation, ConversationParticipant, Message
from .serializers import (
    UserSerializer, UserSummarySerializer,
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    
    def get_serializer_class(self):
        return ConversationListSerializer if self.action == 'list' else ConversationSerializer
    
    def get_queryset(self):
        """Return conversations where authenticated user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).distinct().prefetch_related('participants', 'messages__sender')
        
    def perform_create(self, serializer):
        """Includes current user in conversation"""
        participant_ids = self.request.data.get('participant_ids', [])
        
        #Adds current user to participants
        current_user_id = str(self.request.user.user_id)
        if current_user_id not in participant_ids:
            participant_ids.append(current_user_id)
            
        serializer.save(participant_ids=participant_ids)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get conversation messages with pagination"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('-sent_at')
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    
    def get_serializer_class(self):
        return MessageCreateSerializer if self.action == 'create' else MessageSerializer
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Message.objects.none() 
        
        user_conversations = Conversation.objects.filter(participants__id=self.request.user.id)
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').order_by('-sent_at')
        
    def perform_create(self, serializer):
        """Validate user in participant before creating message"""
        conversation_id = self.request.data.get('conversation')
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
        
    def check_message_ownership(self, message):
        """Helper method to check if user owns the message"""
        if message.sender != self.request.user:
            return Response(
                {'error': 'You can only modify your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        return None
    
    def update(self, request, *args, **kwargs):
        """Update message (only sender can edit)"""
        message = self.get_object()
        ownership_check = self.check_message_ownership(message)
        if ownership_check:
            return ownership_check

        message.is_edited = True
        message.save(update_fields=['is_edited', 'edited_at'])
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete message (only sender can delete)"""
        message = self.get_object()
        ownership_check = self.check_message_ownership(message)
        if ownership_check:
            return ownership_check
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=['is_read'])
        return Response(MessageSerializer(message).data)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread_messages = self.get_queryset().filter(
            is_read=False
        ).exclude(sender=request.user)
        
        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)
    
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]
    # lookup_field = 'user_id'
    filter_backends = [filters.SearchFilter]
    
    def get_queryset(self):
        # if not self.request.user.is_authenticated:
        #     return User.objects.none()      
        
        queryset = super().get_queryset().exclude(id=self.request.user.user_id)
        search = self.request.query_params.get('search')
        search_fields = ['email', 'first_name', 'last_name']
        
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        return Response(UserSerializer(request.user).data)