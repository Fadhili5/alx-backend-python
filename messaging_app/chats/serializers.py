from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Conversation, ConversationParticipant, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model with password handling
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'user_id': {'read_only': True},
            'created_at': {'read_only': True},
        }
        
    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs.get('password') != attrs.get('confirmation_password'):
            raise serializers.ValidationError("Passwords and confirm passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password
        """
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user =User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserSummarySerializer(serializers.ModelSerializer):
    """
    User serializer for nested relationships
    """
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'role']
        
class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for message model
    """
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation',
            'message_body', 'sent_at', 'is_read', 'is_edited', 'edited_at'
        ]
        extra_kwargs = {
            'message_id': {'read_only': True},
            'sent_at': {'read_only': True},
            'edited_at': {'read_only': True},
        }
        
    def validate_sender_id(self, value):
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender ID.")
        return value

class ConversationParticipantSerializer(serializers.ModelSerializer):
    participant = UserSummarySerializer(read_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = ['participant', 'joined_at', 'is_active']
        
class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    conversation_participants = ConversationParticipantSerializer(many=True, read_only=True)
    participants = UserSummarySerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'conversation_participants', 'messages',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'conversation_id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        
    def validate_participant_ids(self, value):
        """
        Validate participants IDs exist and minimum of 2 participants
        """
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 participants are required.")
        
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("Invalid participant IDs.")
        
        return value
    
    def create(self, validated_data):
        """ 
        Create conversations with participants
        """
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        for participant_id in participant_ids:
            user = User.objects.get(user_id=participant_id)
            ConversationParticipant.objects.create(
                conversation=conversation,
                participant=user
            )
            
        return conversation
    
class ConversationListSerializer(serializers.ModelSerializer):
    """ 
    Serializer for conversation list without nested messages
    """
    participants = UserSummarySerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'last_message',
            'message_count', 'created_at', 'updated_at'
        ]
        
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.first_name
            }
        return None
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating messages
    """
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']
        
    def create(self, validated_data):
        """
        create message with sender from request context
        """
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)