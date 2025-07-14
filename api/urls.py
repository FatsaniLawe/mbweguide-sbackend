from django.urls import path
from .views import (
    RecommendCropView,
    HealthCheckView,
    CommunityChatHistoryView,
    ChatbotView,
    ExpertSystemView,
)

urlpatterns = [
    path('recommend-crop/', RecommendCropView.as_view(), name='recommend-crop'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('community-chat-history/', CommunityChatHistoryView.as_view(), name='community-chat-history'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('expert-system/', ExpertSystemView.as_view(), name='expert-system'),
]