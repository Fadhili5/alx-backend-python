from django.urls import path, include
from rest_framework import routers as nested_routers
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'users', UserViewSet, basename='users')

conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]